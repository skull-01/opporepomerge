"""Reconnect backoff helper (v1.0.7).

Pure functions only - no sockets, no threads, no Kodi imports - so the
schedule can be unit-tested deterministically with mocks for randomness
and time.
"""

from __future__ import annotations

import random
from collections.abc import Callable

DEFAULT_BASE_DELAY = 1.0  # seconds
DEFAULT_CAP_DELAY = 30.0  # seconds (per-step cap)
DEFAULT_MAX_RETRIES = 8  # 0 means "do not retry"
DEFAULT_JITTER = 0.25  # +/- 25 percent jitter on each delay


def compute_delay(
    attempt: int,
    base: float = DEFAULT_BASE_DELAY,
    cap: float = DEFAULT_CAP_DELAY,
    jitter: float = DEFAULT_JITTER,
    rng: Callable[[], float] | None = None,
) -> float:
    """Return the delay (seconds, float) before retry attempt N (1-based).

    Uses exponential backoff: base * 2**(attempt-1), capped at `cap`,
    then a symmetric jitter applied as a multiplicative factor in
    [1 - jitter, 1 + jitter].  When `jitter` is 0, the delay is fully
    deterministic (useful in tests).

    `rng` is an optional callable returning a float in [0, 1).  Defaults
    to random.random.
    """
    if attempt < 1:
        attempt = 1
    raw: float = float(base) * (2 ** (attempt - 1))
    if raw > cap:
        raw = cap
    if not jitter:
        return raw
    if rng is None:
        rng = random.random
    # rng() in [0,1) -> factor in [1-j, 1+j]
    factor = (1.0 - jitter) + (rng() * 2.0 * jitter)
    val = raw * factor
    if val < 0:
        val = 0.0
    return val


def schedule(
    max_retries: int = DEFAULT_MAX_RETRIES,
    base: float = DEFAULT_BASE_DELAY,
    cap: float = DEFAULT_CAP_DELAY,
    jitter: float = 0.0,
    rng: Callable[[], float] | None = None,
) -> list[float]:
    """Return the full deterministic delay schedule [d1, d2, ..., dN].

    Defaults to jitter=0 so callers (and tests) get the exact exponential
    schedule.  Set jitter > 0 to get a sampled schedule.
    """
    return [
        compute_delay(i, base=base, cap=cap, jitter=jitter, rng=rng)
        for i in range(1, int(max_retries) + 1)
    ]


def should_retry(attempt: int, max_retries: int = DEFAULT_MAX_RETRIES) -> bool:
    """True if another retry should be attempted after this failure."""
    return attempt < int(max_retries)
