# CEC Control Experiment

**An experiment: no-blip OPPO playback with pure, spec-legitimate HDMI-CEC switching -- no IR, no spoofing.**

A fork of [OppoKodiBridge v3](https://github.com/skull-01/OppoKodiBridge-v3) (the playercorefactory no-blip
variant), itself a fork of [v2](https://github.com/skull-01/OppoKodiBridge). It keeps v3's external-player
handoff (so Kodi never starts the file and there is no pre-play "blip") but strips the IR blaster and switches
the TV using **only legitimate CEC**.

## The hypothesis

Clean two-way TV input switching with **zero extra hardware and zero CEC-bus corruption**, by using CEC the
way the spec intends -- each device announcing its *own* active source -- and accepting the OPPO power-cycle
as the cost.

| Leg | How |
|-----|-----|
| OPPO grabs its HDMI input | the OPPO's **own** One-Touch-Play, forced by power-cycling it (`#POF`->`#PON`). It only asserts active source on a power-**ON** transition, so an already-on OPPO is power-cycled to re-grab. |
| Kodi reclaims its HDMI input | Kodi re-asserts its **own** active source (libCEC `SetActiveSource`). |

**Never:** an IR blaster, a CEC `<Active Source>` / `<Set Stream Path>` injected with a *foreign* initiator,
or a second `cec-client` / `cec-ctl` owner -- those corrupt the shared CEC bus (the verified root cause of the
Mi Box cross-control that motivated this fork).

### Assert once per event -- never re-assert

Each TV-input assertion is **single-shot, tied to an event**: the OPPO grabs HDMI-1 once on play, Kodi
reclaims once on stop. There is **no standing monitor** re-asserting active source -- that would override a
manual input change and make the TV un-leaveable (CEC is open-loop; it can't tell "the TV missed my frame"
from "the user switched away"). So if you manually switch the TV input, your choice **stays**. The reclaim is
single-shot by construction (`service.oppokodibridge.cec/resources/lib/cec_reclaim.py`): a request is consumed
once and removed before it fires.

### Why this is the *legitimate* path (primary sources)

HDMI-CEC has no "give-back" and only two routing primitives: `<Active Source>` (a device announces **its own**
source) and `<Set Stream Path>` (**TV-only**). So no third party may drive the TV to the OPPO's input -- the
only in-spec lever is the OPPO's own One-Touch-Play. See the Linux kernel CEC framework docs and libCEC's own
enforcement (`"only the TV is allowed to send CEC_OPCODE_SET_STREAM_PATH"`).

## Trade-off

The OPPO power-cycle costs **~20-24 s** on every handoff -- the deliberate price for no IR hardware and a clean
bus. (v2 = CEC but blips; v3 = no blip but needs IR; this = no blip, pure CEC, slow grab.)

## Status

Experimental, software-verified only. Pure-logic tests run off-box: `python -m pytest -q`. Installs alongside
v2 and v3 (add-on id `service.oppokodibridge.cec`) for direct A/B/C comparison.

- **PR1:** fork of v3 with IR removed; switching reduced to power-cycle (play) + a reclaim stub (stop).
- **PR3 (done):** explicit **single-shot** Kodi reclaim -- `pcf_player` drops a one-shot request when the handoff ends; the in-Kodi service consumes it once and calls `CECActivateSource`. Never a standing re-asserter.
- **PR2:** make the power-cycle unconditional (cover the already-on case every time).
- **PR4:** experiment harness + measurements (grab/reclaim latency, blip, bus-clean) vs v2 / v3.

## License

MIT -- see [LICENSE](LICENSE).
