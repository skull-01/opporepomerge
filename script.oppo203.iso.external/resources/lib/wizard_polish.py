"""Wizard polish (v1.1.1).

Pure-function model of the wizard's navigation, in-step Test-Now,
pre-apply Summary, and Dry-run-no-write guarantee.  The real Kodi
wizard wraps this module; tests drive it directly.

Public API
----------
- STEPS: ordered tuple of step ids.
- WizardState(values=None, dry_run=False, step_index=0)
- next_step(state)            -> WizardState
- prev_step(state)            -> WizardState  (Back; clamps at 0)
- can_go_back(state)          -> bool
- can_go_next(state)          -> bool
- test_now(state, *, probe)   -> dict        (in-step connection test)
- summary(state)              -> list[(key, value)] for the Summary page
- apply(state, *, writer)     -> dict        ({"written": bool, "values": {...}})
                                  writes only when dry_run=False
"""

from copy import deepcopy


STEPS = (
    "welcome",       # 0  intro / language pick
    "connection",    # 1  IP, port, Test-Now lives here
    "hardware",      # 2  preset + start/stop commands
    "autopoweron",   # 3  master toggle + delay
    "wizard_mode",   # 4  Basic / Full
    "summary",       # 5  pre-apply review
    "done",          # 6  applied (or dry-run reported)
)


class WizardState(object):
    """Lightweight, picklable, copy-on-write wizard state container."""

    __slots__ = ("values", "dry_run", "step_index", "history", "last_test")

    def __init__(self, values=None, dry_run=False, step_index=0):
        self.values = dict(values) if values else {}
        self.dry_run = bool(dry_run)
        self.step_index = int(step_index)
        # Stack of step_index values we've visited (for Back).
        self.history = []
        self.last_test = None

    def copy(self):
        c = WizardState(values=self.values, dry_run=self.dry_run,
                        step_index=self.step_index)
        c.history = list(self.history)
        c.last_test = (None if self.last_test is None
                       else dict(self.last_test))
        return c

    @property
    def step(self):
        if 0 <= self.step_index < len(STEPS):
            return STEPS[self.step_index]
        return None

    def __eq__(self, other):
        if not isinstance(other, WizardState): return NotImplemented
        return (self.values == other.values
                and self.dry_run == other.dry_run
                and self.step_index == other.step_index
                and self.history == other.history)


def can_go_back(state):
    return state.step_index > 0


def can_go_next(state):
    return state.step_index < len(STEPS) - 1


def next_step(state):
    if not can_go_next(state):
        return state.copy()
    new = state.copy()
    new.history.append(state.step_index)
    new.step_index += 1
    return new


def prev_step(state):
    """Back navigation. Pops history if available; otherwise clamps."""
    if not can_go_back(state):
        return state.copy()
    new = state.copy()
    if new.history:
        new.step_index = new.history.pop()
    else:
        new.step_index -= 1
    return new


def test_now(state, *, probe):
    """In-step connection test on the connection step.

    `probe(host, port)` is injected; tests pass a stub.  Returns the
    probe result, also stored on the returned state's `last_test`.
    Raises RuntimeError if called from a non-connection step.
    """
    if state.step != "connection":
        raise RuntimeError("test_now only valid on the connection step, "
                           "current step is " + str(state.step))
    host = state.values.get("oppo_ip", "")
    port = state.values.get("oppo_port", 23)
    try:
        result = probe(host, int(port))
        if not isinstance(result, dict):
            result = {"ok": bool(result)}
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}
    new = state.copy()
    new.last_test = result
    return new


def summary(state):
    """Return a deterministic list of (key, value) tuples for review."""
    items = sorted(state.values.items(), key=lambda kv: kv[0])
    return list(items) + [("__dry_run__", state.dry_run)]


def apply(state, *, writer):
    """Apply settings via injected writer.

    `writer(key, value)` is the persistence sink; tests pass a stub
    that records calls.  When dry_run=True, the writer is NOT called
    and the returned dict carries `written=False`.
    """
    if state.dry_run:
        return {"written": False, "values": deepcopy(state.values),
                "dry_run": True, "writer_calls": 0}
    n = 0
    for k, v in state.values.items():
        writer(k, v)
        n += 1
    return {"written": True, "values": deepcopy(state.values),
            "dry_run": False, "writer_calls": n}
