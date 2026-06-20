"""Off-box tests for the single-shot CEC-reclaim signalling -- and the NEVER-REASSERT invariant."""
import os
import tempfile

from resources.lib import cec_reclaim


def test_request_then_consume_fires_exactly_once():
    with tempfile.TemporaryDirectory() as d:
        assert cec_reclaim.request(d) is True
        fired = []
        assert cec_reclaim.consume(d, lambda: fired.append(1)) is True
        assert fired == [1]
        # the flag is gone -> a second consume does NOT fire again (single-shot per request)
        assert cec_reclaim.consume(d, lambda: fired.append(1)) is False
        assert fired == [1]


def test_consume_without_request_never_fires():
    # THE never-reassert invariant: with no pending request, the service asserts NOTHING. Repeated
    # polling must never assert active source on its own (otherwise it would fight a manual switch).
    with tempfile.TemporaryDirectory() as d:
        fired = []
        for _ in range(5):
            assert cec_reclaim.consume(d, lambda: fired.append(1)) is False
        assert fired == []


def test_flag_removed_before_fire_so_an_error_cannot_refire():
    with tempfile.TemporaryDirectory() as d:
        cec_reclaim.request(d)

        def boom():
            raise RuntimeError("CEC failed")

        try:
            cec_reclaim.consume(d, boom)
        except RuntimeError:
            pass
        # the request was cleared before fire() ran -> no leftover flag, no re-fire loop
        assert not os.path.exists(os.path.join(d, cec_reclaim.RECLAIM_FLAG))
        fired = []
        assert cec_reclaim.consume(d, lambda: fired.append(1)) is False
        assert fired == []


def test_discard_removes_a_stale_flag_without_firing():
    # Startup purge: a flag present at service start (left over across a restart) is dropped WITHOUT
    # asserting -- it must NOT fire CECActivateSource at boot and override a manual input choice.
    with tempfile.TemporaryDirectory() as d:
        cec_reclaim.request(d)
        cec_reclaim.discard(d)
        assert not os.path.exists(os.path.join(d, cec_reclaim.RECLAIM_FLAG))
        fired = []
        assert cec_reclaim.consume(d, lambda: fired.append(1)) is False
        assert fired == []


def test_discard_is_a_noop_without_a_flag():
    with tempfile.TemporaryDirectory() as d:
        cec_reclaim.discard(d)  # must not raise when there is nothing to drop
