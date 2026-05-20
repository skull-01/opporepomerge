"""Tiny loopback fake OPPO TCP server for MVP integration tests."""

import socket
import threading
import time


class FakeOppoServer:
    """A small TCP server bound to 127.0.0.1 with an ephemeral port.

    responses may be a dict mapping command strings (without CR/LF) to response
    lines, or a callable(command, index) -> response. The server records every
    command it receives and sends CR-terminated response lines.
    """

    def __init__(self, responses=None, push_lines=None, close_after_commands=None):
        self.host = "127.0.0.1"
        self.responses = responses or {}
        self.push_lines = list(push_lines or [])
        self.close_after_commands = close_after_commands
        self.commands = []
        self._stop = threading.Event()
        self._ready = threading.Event()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, 0))
        self.port = self._sock.getsockname()[1]
        self._sock.listen(8)
        self._thread = threading.Thread(target=self._serve, daemon=True)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def start(self):
        self._thread.start()
        self._ready.wait(1.0)
        return self

    def close(self):
        self._stop.set()
        try:
            with socket.create_connection((self.host, self.port), timeout=0.2):
                pass
        except OSError:
            pass
        try:
            self._sock.close()
        except OSError:
            pass
        self._thread.join(timeout=1.0)

    def _response_for(self, command, index):
        if callable(self.responses):
            return self.responses(command, index)
        return self.responses.get(command, "@OK")

    def _serve(self):
        self._ready.set()
        while not self._stop.is_set():
            try:
                client, _addr = self._sock.accept()
            except OSError:
                break
            threading.Thread(target=self._handle, args=(client,), daemon=True).start()

    def _handle(self, client):
        with client:
            client.settimeout(1.0)
            count = 0
            buf = b""
            try:
                while not self._stop.is_set():
                    chunk = client.recv(1024)
                    if not chunk:
                        break
                    buf += chunk
                    while b"\r" in buf or b"\n" in buf:
                        positions = [p for p in (buf.find(b"\r"), buf.find(b"\n")) if p >= 0]
                        idx = min(positions)
                        raw = buf[:idx]
                        sep_len = 2 if buf[idx:idx+2] == b"\r\n" else 1
                        buf = buf[idx + sep_len:]
                        command = raw.decode("ascii", errors="replace").strip()
                        if not command:
                            continue
                        self.commands.append(command)
                        count += 1
                        response = self._response_for(command, count)
                        if response is not None:
                            client.sendall((str(response).rstrip("\r\n") + "\r").encode("ascii"))
                        if self.push_lines:
                            for line in self.push_lines:
                                time.sleep(0.01)
                                client.sendall((str(line).rstrip("\r\n") + "\r").encode("ascii"))
                        if self.close_after_commands and count >= self.close_after_commands:
                            return
            except OSError:
                return
