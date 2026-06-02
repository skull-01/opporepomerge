"""Property-based robustness tests for the Xnoppo V3 pure predicates + HDMI sequencing.

These complement the example-based tests in test_oppo_http_pure.py / test_hdmi_sequencing.py.
The status/info predicates accept *arbitrary* device responses (dicts, strings, junk), so the
invariant under test is "never raises, always returns a bool" across a wide input space -- the
class of latent bug that hand-picked examples miss (cf. v1.1.9, where property tests surfaced
three real crashes). Hypothesis is used when installed; otherwise the same invariants run against
a curated deterministic sample so the gate never silently weakens.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "resources" / "lib"
for _path in (str(ROOT), str(LIB)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from resources.lib.kodi import hdmi_sequencing as hs
from resources.lib.oppo import oppo_control as oc

try:
    from hypothesis import given
    from hypothesis import settings as hyp_settings
    from hypothesis import strategies as st

    HAVE_HYPOTHESIS = True
except ImportError:  # pragma: no cover - only on minimal images without Hypothesis
    HAVE_HYPOTHESIS = False


# The single-argument predicates that must tolerate ANY device response without raising.
PREDICATES = (
    oc.tcp_qpl_is_idle,
    oc.http_status_is_idle,
    oc.http_info_is_definitive_stop,
    oc.http_info_indicates_playing,
    oc.global_info_is_playing,
)

# A curated cross-section of "weird but legal" inputs for the no-Hypothesis fallback path. The
# inf/nan-bearing dicts specifically exercise the int(value) coercion inside the play-status
# helpers, where int(float("inf")) raises OverflowError (not Value/TypeError).
CURATED = (
    None,
    "",
    "   ",
    "PLAYING",
    "stop",
    0,
    1,
    -1,
    10**9,
    1.5,
    float("inf"),
    float("-inf"),
    float("nan"),
    True,
    False,
    b"bytes",
    [],
    [1, 2, 3],
    {},
    {"x": 1},
    {"e_play_status": float("inf")},
    {"play_status": float("nan")},
    {"result": {"e_play_status": float("inf")}},
    {"playinfo": {"status": float("-inf")}},
    {"is_playing": float("inf")},
    object(),
    ["nested", {"a": {"b": 1}}],
)


def test_predicates_never_raise_on_curated_inputs():
    for fn in PREDICATES:
        for value in CURATED:
            result = fn(value)
            assert isinstance(result, bool), f"{fn.__name__}({value!r}) -> non-bool {result!r}"


def test_compute_play_delay_is_nonneg_int_for_curated_inputs():
    medias = ["", "movie.mkv", "/x/movie.iso", "/x/BDMV/index.bdmv", "weird\x00name"]
    raws = ["0", "2", "-5", "", None, "abc", 7, 1.9, float("nan"), float("inf")]
    for media in medias:
        for raw in raws:
            delay = hs.compute_play_delay(media, raw)
            assert isinstance(delay, int) and delay >= 0
    # ISO/BDMV sources are floored at the disc minimum.
    assert hs.compute_play_delay("/x/movie.iso", "0") >= hs.DISC_MIN_DELAY_SECONDS
    assert hs.compute_play_delay("/x/BDMV/index.bdmv", "1") >= hs.DISC_MIN_DELAY_SECONDS


def test_switch_mode_and_av_stagger_clamp_curated_inputs():
    for raw in ("immediate", "delayed", "DELAYED", "bogus", "", None, 5, 1.5):
        assert hs.switch_mode({"hdmi_switch_mode": raw}) in hs.HDMI_SWITCH_MODES
    for raw in ("0", "10", "-3", "", None, "x", 4, 2.5):
        assert hs.av_stagger({"av_delay_hdmi": raw}) >= 0


if HAVE_HYPOTHESIS:
    _ANY = st.recursive(
        st.one_of(
            st.none(),
            st.booleans(),
            st.integers(),
            st.floats(allow_nan=True, allow_infinity=True),
            st.text(),
            st.binary(),
        ),
        lambda children: st.one_of(
            st.lists(children, max_size=5),
            st.dictionaries(st.text(max_size=12), children, max_size=5),
        ),
        max_leaves=20,
    )

    @hyp_settings(max_examples=200)
    @given(value=_ANY)
    def test_predicates_never_raise_property(value):
        for fn in PREDICATES:
            assert isinstance(fn(value), bool)

    @hyp_settings(max_examples=150)
    @given(
        media=st.text(max_size=80),
        raw=st.one_of(
            st.none(),
            st.text(max_size=12),
            st.integers(),
            st.floats(allow_nan=True, allow_infinity=True),
        ),
    )
    def test_compute_play_delay_property(media, raw):
        delay = hs.compute_play_delay(media, raw)
        assert isinstance(delay, int) and delay >= 0
