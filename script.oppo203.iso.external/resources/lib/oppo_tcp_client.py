"""oppo_tcp_client.py -- v1.0.7 persistent TCP client for Oppo UDP-20X verbose push mode.
v1.0.7 adds reconnect-with-exponential-backoff via wait_for_stop_persistent().

This module provides a minimal persistent TCP connection to the Oppo on port 23,
sends #SVM 2 (verbose mode 2) on connect, and then reads CR-terminated unsolicited
push messages on a background thread.  The main thread can call wait_for_stop() to
block until a stop/power-off condition is signalled by the Oppo.

Stop conditions recognised:
  @UPW 0          -- power-off event
  @UPL STOP       -- playback stopped
  @UPL HOME       -- home screen (no disc playing)
  @UPL MCTR       -- media centre / no media
  @UPL DISC       -- disc menu (treat as stop; playback not active)
  @UPL NO DISC    -- no disc inserted

Keep-alive conditions (NOT stop):
  @UPL PLAY, @UPL PAUSE, @UPL FFWD, @UPL FREV, @UPL SFWD, @UPL SREV, @UPL LOADING

The client is intentionally simple and safe:
  - All state is local to one OppoTcpClient instance.
  - If the TCP connection fails or drops, wait_for_stop() returns False
    (caller should fall back to polling or log and exit).
  - send_svm is opt-in (default True); disable if the Oppo is already in verbose mode.

Usage in external_player.py hold_playback() verbose_push branch::

    client = OppoTcpClient(host, port)
    stopped = client.wait_for_stop(timeout=14400)   # 4 hours
    # stopped=True  -> @UPW 0 or @UPL STOP/* received
    # stopped=False -> timed out or connection failed (caller should exit anyway)
"""

import socket
import threading
import time


# Push message prefixes that signal playback has stopped or the device is idle.
_UPL_STOP_VALUES = {
    "STOP",
    "STOPPED",
    "HOME",
    "HOME MENU",
    "MCTR",
    "MEDIA CENTER",
    "DISC",
    "DISC MENU",
    "NO DISC",
    "NODISC",
}

# Push message values that mean playback is ongoing (NOT a stop condition).
_UPL_PLAY_VALUES = {
    "PLAY",
    "PAUSE",
    "FFWD",
    "FREV",
    "SFWD",
    "SREV",
    "LOADING",
}


class OppoTcpClient:
    """Minimal persistent TCP client for Oppo UDP-20X verbose push messages.

    Connects to host:port, optionally sends #SVM 2, then reads lines in a
    background thread.  Call wait_for_stop(timeout) to block until a stop
    condition is received or the timeout expires.
    """

    def __init__(self, host, port, send_svm=True, svm_mode=2, recv_timeout=5.0):
        self._per_attempt_timeout = 14400
        self._host = host
        self._port = int(port)
        self._send_svm = bool(send_svm)
        self._svm_mode = int(svm_mode)
        self._recv_timeout = float(recv_timeout)
        self._stopped = threading.Event()
        self._connected = threading.Event()
        self._connection_closed = threading.Event()
        self._stop_event_seen = False
        self._error = None
        self._sock = None
        self._thread = None

    def _connect_and_read(self):
        """Background thread: connect, set verbose mode, read push lines."""
        try:
            sock = socket.create_connection((self._host, self._port), timeout=10.0)
            self._sock = sock
            sock.settimeout(self._recv_timeout)
            self._connected.set()

            if self._send_svm:
                cmd = f"#SVM {self._svm_mode}\r".encode("ascii")
                sock.sendall(cmd)
                # Read and discard the #SVM response line (best-effort)
                try:
                    sock.recv(256)
                except (socket.timeout, OSError):
                    pass

            buf = b""
            while not self._stopped.is_set():
                try:
                    chunk = sock.recv(1024)
                    if not chunk:
                        # Connection closed by remote
                        break
                    buf += chunk
                    while b"\r" in buf or b"\n" in buf:
                        # Split on first CR or LF
                        for sep in (b"\r\n", b"\r", b"\n"):
                            idx = buf.find(sep)
                            if idx >= 0:
                                line_bytes = buf[:idx]
                                buf = buf[idx + len(sep):]
                                line = line_bytes.decode("ascii", errors="replace").strip()
                                self._handle_line(line)
                                break
                        else:
                            break
                except socket.timeout:
                    continue
                except OSError:
                    break
        except OSError as exc:
            self._error = exc
            self._connected.set()  # Unblock wait_for_stop so it can detect the failure
        finally:
            self._connection_closed.set()
            if self._sock:
                try:
                    self._sock.close()
                except OSError:
                    pass

    def _handle_line(self, line):
        """Inspect one incoming line for stop/play push events."""
        upper = line.upper().strip()
        if not upper.startswith("@"):
            return

        # @UPW 0 = power off
        if upper.startswith("@UPW"):
            parts = upper.split()
            if len(parts) >= 2 and parts[1] == "0":
                self._stop_event_seen = True
                self._stopped.set()
                return

        # @UPL <value> = playback status change
        if upper.startswith("@UPL"):
            value = upper[4:].strip()
            if value in _UPL_STOP_VALUES:
                self._stop_event_seen = True
                self._stopped.set()

    def wait_for_stop(self, timeout=14400):
        """Block until a real stop push event is received or timeout expires.

        Returns True only when @UPL/@UPW content explicitly signals stop/power
        off. A clean TCP disconnect is a transport failure, not playback stop;
        it returns False so callers can reconnect or fall back to polling.
        """
        self._thread = threading.Thread(
            target=self._connect_and_read, daemon=True, name="OppoTcpPush"
        )
        self._thread.start()

        # Wait until connected (or failed) before entering the main wait.
        self._connected.wait(timeout=15.0)

        if self._error is not None:
            return False

        deadline = time.time() + float(timeout)
        while time.time() < deadline:
            if self._stop_event_seen:
                return True
            if self._error is not None or self._connection_closed.is_set():
                return False
            time.sleep(0.02)
        return False


    def wait_for_stop_persistent(self, timeout=14400, max_retries=8,
                                 base_delay=1.0, cap_delay=30.0,
                                 jitter=0.25, _sleep=None, _rng=None,
                                 _connect_factory=None):
        """Like wait_for_stop, but reconnects on transient failures.

        On each failure we consult `reconnect_backoff.compute_delay` for
        the next sleep, sleep, and try again until either:
            - a stop event is observed (returns True),
            - max_retries failures occur in a row (returns False),
            - the overall timeout elapses (returns False).

        Test-injection points (all optional, keyword-only):
            _sleep:           callable(seconds) -> None        (default time.sleep)
            _rng:             callable() -> float in [0,1)     (default random.random)
            _connect_factory: callable() -> bool               (default self._attempt_once)
                              must return True on success/stop and False on failure.

        Public usage::

            client = OppoTcpClient(host, port)
            stopped = client.wait_for_stop_persistent(timeout=14400, max_retries=8)
        """
        try:
            from . import reconnect_backoff as rb
        except (ImportError, ValueError):
            import reconnect_backoff as rb

        if _sleep is None:
            _sleep = time.sleep
        attempt_fn = _connect_factory or self._attempt_once

        deadline = time.time() + float(timeout) if timeout is not None else None
        attempt = 0
        attempts_made = 0
        while True:
            attempts_made += 1
            ok = False
            try:
                ok = attempt_fn()
            except Exception:
                ok = False
            if ok:
                return True
            attempt += 1
            if not rb.should_retry(attempt, max_retries):
                return False
            delay = rb.compute_delay(
                attempt, base=base_delay, cap=cap_delay,
                jitter=jitter, rng=_rng,
            )
            if deadline is not None:
                remaining = deadline - time.time()
                if remaining <= 0:
                    return False
                if delay > remaining:
                    delay = max(0.0, remaining)
            _sleep(delay)
            if deadline is not None and time.time() >= deadline:
                return False

    def _attempt_once(self):
        """Single connect+wait attempt; returns True on stop, False on failure.

        Reuses the existing wait_for_stop() for behavioural parity, but
        re-creates the per-attempt threading state so retries are clean.
        """
        # Reset per-attempt state so each retry is independent
        import threading as _t
        self._connected = _t.Event()
        self._stopped   = _t.Event()
        self._connection_closed = _t.Event()
        self._stop_event_seen = False
        self._error     = None
        self._sock      = None
        self._thread    = None
        return bool(self.wait_for_stop(timeout=self._per_attempt_timeout))

    def close(self):
        """Request shutdown of the background thread and close the socket."""
        self._stopped.set()
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
