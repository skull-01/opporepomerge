# Configurator v0.9.10 — Build Notes

**Theme:** Developer-mode + wizard **honesty** — make the configurator's "tests" reflect real
device I/O instead of canned/simulated output.

**Bundled add-on:** v2.9.17 (unchanged). **Hardware validation:** software-verified only; not
performed / not claimed. Phase-C steps recorded in
[`docs/MANUAL_VERIFICATION_CHECKLIST.md`](../../../docs/MANUAL_VERIFICATION_CHECKLIST.md).

## What changed

- **OPPO :436 HTTP console signin** (PR #356, merge `42936cf`). The OPPO console's HTTP tab now
  performs the real OREMOTE handshake before commands — UDP `NOTIFY OREMOTE LOGIN` → player `:7624`,
  then `GET /signin?{"appIconType":1,"appIpAddress":<lan-ip>}` — matching the working
  emby-chinoppo-bridge. Previously it fired commands with no session (the player refused them), and
  the only handshake (`oppo_http_play`) used a wrong `0x55`→:436 broadcast + user/password signin;
  both corrected. TCP (:23) path untouched.
- **Per-device reachability ping** (ENH #358, PR #357). New `ping_host` Tauri command (real
  TCP-connect latency) + a shared `PingRow`, wired into the Kodi / TV / AVR / NAS dev panels.
- **Step 1 connection checks** (#353, PR #357). The SSH/SMB check rows show the **entered IP** + the
  **real** probe result (ping latency + `ssh_test` key auth; `smb_test_write` writable) instead of a
  hardcoded `10.0.1.42` and fabricated OpenSSH/fingerprint/ICMP detail.
- **Find on network** (#354, PR #357). Wired the dead button to the real `scan_kodi_hosts`; picking
  a discovered box sets the IP. The fake `10.0.1.42` input default is gone.
- **Step 4 TV mute test** (#355, PR #357). Sends a **real** mute (`ping_host` + Roku `VolumeMute` /
  adb `KEYCODE_VOLUME_MUTE`) and reports the true result — no more `setTimeout` fake
  "command transmitted · 124 ms".

## Gate (software-verified)

- `npx tsc --noEmit` — clean
- `npx vitest run` — **361 passed**
- `cargo test` — **57 passed**
- `npm run build` (vite) — OK
- `npm run dist` (MSI + NSIS) — built for this release

## Artifacts

- `Kodi Oppo External Player Configurator_0.9.10_x64_en-US.msi`
- `Kodi Oppo External Player Configurator_0.9.10_x64-setup.exe` (NSIS)
- `SHA256SUMS.txt`

Published via `scripts/release-configurator-local.ps1` as `configurator-v0.9.10` (repo Latest).
