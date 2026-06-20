"""Architecture benchmarking (v1.0.8).

Replaces the v1.0.3 heuristic auto-test with measured probes.

For each candidate architecture we time 3 trials of a representative
operation and recommend by the median.  All time-bound work is injected
through the `timer` callable so the suite is fully unit-testable
without sockets, files, or wall-clock waits.

Public API
----------
- TRIALS                    -> int, default 3
- benchmark(candidate, ...) -> dict {"trials":[...], "median": float}
- run_full(...)             -> dict {"external": {...}, "service": {...},
                                     "recommendation": "external"|"service"|"tie",
                                     "playercorefactory_ok": bool}
- recommend(ext_median, svc_median, eps=0.0) -> str
- validate_playercorefactory(path) -> (ok: bool, reason: str)

Lower median wins.  Ties (within `eps`) prefer External Player as the
historically more deterministic path on Chinoppo-class hardware.
"""

from __future__ import annotations

import statistics
import time as _time
from collections.abc import Callable, Iterable
from typing import Any

TRIALS = 3
DEFAULT_EPS = 0.020  # 20 ms - inside this margin the result is considered a tie


def _median(values: Iterable[float]) -> float:
    return float(statistics.median(values))


def benchmark(
    candidate: str,
    trials: int = TRIALS,
    probe: Callable[[str], object] | None = None,
    timer: Callable[[], float] | None = None,
) -> dict[str, Any]:
    """Run `trials` timed probes for `candidate` and return the result.

    `probe`  is a callable(candidate) -> None.  It is expected to perform
             one full handoff (connect, send command, await ack).
    `timer`  is a no-arg callable returning a monotonic float (seconds).
             Defaults to `time.monotonic`.
    """
    if probe is None:
        raise ValueError("benchmark() requires a probe callable")
    if timer is None:
        timer = _time.monotonic
    samples: list[dict[str, Any]] = []
    for _ in range(int(trials)):
        t0 = timer()
        try:
            probe(candidate)
            ok = True
        except Exception:
            ok = False
        t1 = timer()
        dt = max(0.0, float(t1 - t0))
        # On failure we still record the elapsed time so a permanently
        # broken candidate gets a high (bad) median rather than skewing
        # comparison with omitted samples.
        samples.append({"elapsed": dt, "ok": ok})
    elapsed = [s["elapsed"] for s in samples]
    return {
        "candidate": candidate,
        "trials": samples,
        "median": _median(elapsed),
        "all_ok": all(s["ok"] for s in samples),
    }


def recommend(ext_median: float | None, svc_median: float | None, eps: float = DEFAULT_EPS) -> str:
    """Return 'external', 'service', or 'tie' given two medians."""
    if ext_median is None and svc_median is None:
        return "tie"
    if ext_median is None:
        return "service"
    if svc_median is None:
        return "external"
    diff = float(ext_median) - float(svc_median)
    if abs(diff) <= float(eps):
        return "tie"
    return "external" if ext_median < svc_median else "service"


def validate_playercorefactory(path: str | None) -> tuple[bool, str]:
    """Return (ok, reason).

    ok = True only if the file exists, is well-formed XML, and contains
    a <playercorefactory> root with at least one <player> child.
    """
    if not path:
        return (False, "no path provided")
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as exc:
        return (False, "read error: " + str(exc))
    if not data.strip():
        return (False, "empty file")
    try:
        import xml.etree.ElementTree as ET

        root = ET.fromstring(data)
    except Exception as exc:
        return (False, "not well-formed XML: " + str(exc))
    tag = root.tag.split("}")[-1].lower()
    if tag != "playercorefactory":
        return (False, "root element is <" + root.tag + ">, expected <playercorefactory>")
    players = [c for c in root if c.tag.split("}")[-1].lower() == "players"]
    if not players:
        return (False, "no <players> block")
    if not any(c.tag.split("}")[-1].lower() == "player" for c in players[0]):
        return (False, "no <player> child")
    return (True, "ok")


def run_full(
    probe_external: Callable[[str], object],
    probe_service: Callable[[str], object],
    trials: int = TRIALS,
    timer: Callable[[], float] | None = None,
    eps: float = DEFAULT_EPS,
    playercorefactory_path: str | None = None,
) -> dict[str, object]:
    """Run a full benchmark for both architectures and pick a winner.

    Both probes are injected so production callers can wire them to
    real OPPO interactions while tests pass in deterministic stubs.
    """
    ext = benchmark("external", trials=trials, probe=probe_external, timer=timer)
    svc = benchmark("service", trials=trials, probe=probe_service, timer=timer)
    rec = recommend(
        ext["median"] if ext["all_ok"] else None, svc["median"] if svc["all_ok"] else None, eps=eps
    )
    pcf_ok, pcf_reason = (True, "skipped")
    if playercorefactory_path:
        pcf_ok, pcf_reason = validate_playercorefactory(playercorefactory_path)
    return {
        "external": ext,
        "service": svc,
        "recommendation": rec,
        "playercorefactory_ok": pcf_ok,
        "playercorefactory_reason": pcf_reason,
        "eps": float(eps),
        "trials": int(trials),
    }
