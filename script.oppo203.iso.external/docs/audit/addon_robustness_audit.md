# Addon robustness-bug audit + Phase-C runbook

**Scope:** the seven open `area:addon` robustness issues whose fixes are already **merged to
`main`**. This is a ground-truth audit — for each, it confirms the fix exists in the current code
(`file:line`) and is pinned by a passing test, then gives the exact on-device steps the operator
runs for **Phase C** (the only step that authorizes closing the issue).

**What "confirmed fixed in code" means / does not mean:** the change is on `main` and a regression
test pins it. It is **not** a hardware-validation claim — the judgment constants (the 5-failure
abort, the `tcp_qpl_poll` default, the 6 h staleness, the 436 probe port) still need to behave
correctly against a real OPPO + NAS. That is what the Phase-C steps below verify.

**Audited from `main` (this session re-ran the tests):** `pytest tests/test_hold_robustness.py
tests/test_hold_default.py tests/test_session_sentinel_staleness.py tests/test_oppo_status_probe.py`
→ **24 passed**. No `resources/` code was changed by this audit (docs only).

## Summary

| Issue | Was | Merged | Code anchor | Pinned by | Status |
|---|---|---|---|---|---|
| #111 | diag HTTP probe hit port 80 | #132 `bd0cc42` | `oppo_http_port` default `436` ([settings.xml:19](../../resources/settings.xml#L19)); diag reads it ([installer.py:794](../../resources/lib/kodi/installer.py#L794)) | `test_oppo_status_probe.py` | ✅ fixed in code |
| #112 | `verbose_push` failure degraded badly | #129 `396634c` | fallback to `tcp_qpl_poll` ([external_player.py:373](../../resources/lib/kodi/external_player.py#L373)) | `test_hold_robustness.py` | ✅ fixed in code |
| #114 | blind 180-min default hold | #130 `523eadc` | `hold_mode` default `3`=`tcp_qpl_poll` ([settings.xml:164](../../resources/settings.xml#L164)) | `test_hold_default.py` | ✅ fixed in code |
| #115 | `manual_file` waited forever | #129 `396634c` | ceiling deadline ([external_player.py:382](../../resources/lib/kodi/external_player.py#L382)) | `test_hold_robustness.py` | ✅ fixed in code |
| #116 | poll ran 240 min after OPPO loss | #129 `396634c` | `MAX_CONSECUTIVE_POLL_FAILURES=5` abort ([external_player.py:252](../../resources/lib/kodi/external_player.py#L252), [:332](../../resources/lib/kodi/external_player.py#L332)) | `test_hold_robustness.py` | ✅ fixed in code |
| #117 | stale sentinel stuck the bridge | #131 `29d951f` | `session_is_active` 6 h self-heal ([settings_reader.py:29](../../resources/lib/kodi/settings_reader.py#L29)) | `test_session_sentinel_staleness.py` | ✅ fixed in code |
| #123 | `ruff format --check` red on `main` | #133 `43207ba` | format-only; CI lint green | `ruff format --check .` | ✅ fixed in code |

**Audit conclusion:** all seven are genuinely addressed in the merged code — no gap found. Each
remains **open** pending the operator's Phase-C device verification below.

---

## #111 — diagnostic HTTP probe used port 80, not 436

- **Was:** the discovery/diagnostic HTTP probe hit port 80; OPPO's HTTP control API listens on 436.
- **Fix (`#132` `bd0cc42`):** the diag reads `oppo_http_port` (default `436`) — [installer.py:794](../../resources/lib/kodi/installer.py#L794); the HTTP API URL builder uses the same setting ([oppo_control.py:324](../../resources/lib/oppo/oppo_control.py#L324), [:350](../../resources/lib/oppo/oppo_control.py#L350)); `probe_player_status` at [oppo_control.py:699](../../resources/lib/oppo/oppo_control.py#L699).
- **Phase C (on the box):** run the add-on's **"Probe OPPO player status (diagnostic)"** menu action against the real OPPO. **Expect:** the probe targets `:436` (not `:80`) and returns a player-status payload (or a clean timeout if HTTP is off), with no port-80 attempt in the log. **Record:** the probe output + whether HTTP API was reachable.

## #112 — `verbose_push` failure degraded badly

- **Was:** when the persistent verbose-push TCP listener failed, the hold did not degrade gracefully.
- **Fix (`#129` `396634c`):** `hold_playback`'s `verbose_push` branch wraps the listener in `try/except` and **falls back to `_hold_tcp_qpl_poll`** on any failure — [external_player.py:343-376](../../resources/lib/kodi/external_player.py#L343) (fallback at [:373](../../resources/lib/kodi/external_player.py#L373)).
- **Phase C (on the box):** set `hold_mode=verbose_push`, then make the verbose listener fail (e.g. block TCP :23 mid-session or point at an unreachable host). **Expect:** the log shows `falling back to tcp_qpl_poll` and the hold still ends correctly on stop — no hang. **Record:** the fallback log line + that playback-end was detected.

## #114 — blind 180-minute default hold

- **Was:** the default `hold_mode` was `fixed_timeout` (a blind 180-minute sleep regardless of real playback).
- **Fix (`#130` `523eadc`):** the default is now `tcp_qpl_poll` — `hold_mode` `default="3"` ([settings.xml:164](../../resources/settings.xml#L164)) — which actively polls `#QPL` and ends when the player reports idle. The 180-min fixed timeout remains only when explicitly selected ([external_player.py:399](../../resources/lib/kodi/external_player.py#L399)).
- **⚠️ Migration nuance:** this changes the **default** for fresh installs. An existing deployment whose `settings.xml` already persisted `hold_mode=fixed_timeout` keeps it — so for an upgrade, confirm the deployed value (the configurator writes it).
- **Phase C (on the box):** on a fresh/ reconfigured install, confirm the effective `hold_mode` is `tcp_qpl_poll`, then play and **stop** a disc. **Expect:** the hold ends within a couple of poll intervals of the real stop — not after a fixed 180 min. **Record:** time from stop to hold-end + the effective `hold_mode`.

## #115 — `manual_file` hold waited forever

- **Was:** `manual_file` mode waited indefinitely for a stop file that might never appear, pinning Kodi.
- **Fix (`#129` `396634c`):** the wait is bounded by a ceiling deadline (`fixed_timeout_minutes`, default 180) — [external_player.py:382-391](../../resources/lib/kodi/external_player.py#L382).
- **Phase C (on the box):** set `hold_mode=manual_file` and **never** create the stop file. **Expect:** the hold ends at the ceiling (default 180 min) with the log line "reached the N-minute ceiling without a stop file"; creating the stop file earlier ends it immediately. **Record:** that the ceiling fired (a long test — or temporarily lower `fixed_timeout_minutes` to shorten it).

## #116 — polling continued ~240 min after the OPPO was lost

- **Was:** if the OPPO became unreachable mid-hold, the poll kept retrying until the full timeout (~240 min).
- **Fix (`#129` `396634c`):** both poll loops abort after `MAX_CONSECUTIVE_POLL_FAILURES = 5` ([external_player.py:53](../../resources/lib/kodi/external_player.py#L53)) consecutive failures — `tcp_qpl_poll` at [:252](../../resources/lib/kodi/external_player.py#L252), `http_poll` at [:332](../../resources/lib/kodi/external_player.py#L332).
- **Phase C (on the box):** start a poll-mode hold, then pull the OPPO off the network (or block its port). **Expect:** after ~5 failed polls the log says "unreachable for too many consecutive … polls. Ending hold." and the hold ends (does not run to 240 min). **Record:** the abort log line + elapsed time from disconnect to hold-end.

## #117 — a crash left a stale sentinel that stuck the bridge

- **Was:** a crash/power-loss during a hold left `oppo203iso-active` behind, which disabled interception and stuck the remote bridge on the next run.
- **Fix (`#131` `29d951f`):** `session_is_active` treats a sentinel older than `SESSION_MAX_AGE_SECONDS = 21600` (6 h) as inactive, so the next session self-heals — [settings_reader.py:26-46](../../resources/lib/kodi/settings_reader.py#L26).
- **Phase C (on the box):** create a stale `oppo203iso-active` file (touch it with an old mtime, > 6 h) in the add-on's `addon_data` dir, then start a normal playback. **Expect:** the stale sentinel is ignored (interception/bridge behave normally), not treated as a live session. **Record:** that a > 6 h sentinel did not block the new session, and a fresh sentinel (< 6 h) is still honored.

## #123 — `ruff format --check` was red on `main`

- **Was:** three test files had `ruff format` drift — the only red on the CI "Lint and format" job.
- **Fix (`#133` `43207ba`):** the drifted files were reformatted; `ruff format --check .` is clean on `main`.
- **Phase C:** none on hardware — this is a CI/lint fix. Verify by `ruff format --check .` (clean) and a green CI "Lint and format" run. Closeable on that basis alone.
