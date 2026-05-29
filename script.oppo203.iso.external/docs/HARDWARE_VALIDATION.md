# Hardware validation — status and how to help

**Status: software-verified, hardware validation not claimed.** The add-on's device-control
paths are unit-tested against mocks, but they have **not** been confirmed against real
hardware. This page tracks what needs a tester and how you can help. Tracking issue:
[#44](https://github.com/skull-01/script.oppo203.iso.external/issues/44).

## How you can help

1. **Submit a tester report (most valuable, costs nothing).** If you already own any of the
   hardware below, run the relevant path and file a report. Follow
   [CONTRIBUTING.md → Hardware reports](../CONTRIBUTING.md#hardware-reports) for the exact
   fields (add-on version + build, Kodi version + platform, player model + firmware,
   connection method, TV/AVR model, media type + path style, expected vs actual result,
   sanitized logs). Open a GitHub issue with the report. **Never include passwords, tokens,
   Sony PSKs, SmartThings tokens, NAS credentials, or private network details.**
2. **Lend hardware.** A short-term loan of a player / TV / AVR lets a maintainer validate a
   path directly. Open an issue to coordinate.
3. **Donate hardware.** A permanent donation expands what can be kept validated across
   releases. Open an issue to coordinate.

You do not need to lend or donate anything — a single good tester report is the cheapest and
most useful contribution.

## Validation status by device family

Everything below is **software-supported / not hardware-validated** until a tester report is
recorded. "Most wanted" marks the gaps that would help the most.

### Players (OPPO + compatible clones)

| Family | Models with code paths | Status | Notes |
|---|---|---|---|
| OPPO | UDP-203, UDP-205 | tester wanted | reference target; `#PON` wake, `#PLA`/`#STP` |
| Chinoppo (clones) | M9201, M9203, M9205, M9205C, M9200, M9702, "M9205 V1" | **most wanted** | eject-to-wake (`#EJT`) quirk; also confirm whether "M9205 V1" is a distinct device from "M9205" |
| CineUltra | V203, V204 | tester wanted | eject-to-wake posture |
| iPUK | UHD8592 | tester wanted | eject-to-wake posture |
| Giec | BDP-G5300 | tester wanted | eject-to-wake posture |
| Magnetar | UDP800, UDP900 | warning-only | commands not mutated; no compatibility claim |
| Reavon | UBR-X100, UBR-X110, UBR-X200 | warning-only | commands not mutated; no compatibility claim |

### TV input-switching backends

| Backend | Status | Notes |
|---|---|---|
| ADB / Android TV | **most wanted** | port 5555; broadest TV install base |
| Roku ECP | tester wanted | port 8060 probe + `InputHDMIn` |
| Sony Bravia IP | tester wanted | port 20060 |
| LG / Samsung / SmartThings / custom command | tester wanted | command-tier; no port probe |

### AVR sequencing backends

| Backend | Status |
|---|---|
| Denon / Marantz | tester wanted |
| Onkyo (eISCP) | tester wanted |
| Yamaha | tester wanted |
| Sony audio | tester wanted |

## The single most valuable first report

An **OPPO UDP-203 or UDP-205 doing a real UHD-ISO handoff from Kodi** — confirming the
`playercorefactory.xml` routing, the external-player launch, and `#PON`/`#PLA` control over
IP. After that, the **Chinoppo eject-to-wake** path and **ADB TV switching** are the
highest-value gaps.
