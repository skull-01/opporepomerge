# WIP archive — historical §3a / §3b entries

> Moved out of [`AI_RESUME_HANDOFF.md`](../../AI_RESUME_HANDOFF.md) on 2026-06-05 to keep the
> resume-read lean. The live handoff keeps the current clean-slate entry + one prior per area;
> everything older lives here, newest first.

## §3a Addon — archived entries

**As of 2026-06-03 (EOD #20 — add-on `v2.9.16` BUILT + PR [#333](https://github.com/skull-01/script.oppo203.iso.external/pull/333) open, CI GREEN, NOT yet merged/tagged/published).**
**Stopping point: `release/v2.9.16` pushed; PR #333 all checks green (Release gate, configurator Gate, lint, mypy, compat-smoke ×3, claude-review); awaiting merge + tag + publish — the FIRST resume action. `main` still @`5fa1b70` (v2.9.16 not on main yet). Local gate: pytest 1187/3, serial coverage 99% (5899 stmts), mypy --strict 51/0, ruff clean, audit_release PASS 607/607.**
Operator picked the **3-theme override** (Addon 2 + Cfg 1 + Cfg 2), then called `done for the day` mid-release while CI was running. **Addon theme delivered to the PR stage:** cut standalone add-on **v2.9.16** folding the 7 runtime fixes merged since v2.9.15 — AVR `http_handoff` eligibility + HTTP path translation (#221–#224), SVM3/`oppo_control`/eISCP transport hardening (#226–#233), configurator-owned settings schema guards (#235–#237), honest Pure-HTTP launch (#254), distinct Samsung HDMI defaults (#256), coercion fixes (#275/#329). Bumped `version.py` (2.9.15→2.9.16, build 24→25), `pyproject`, `sources.yaml`, `addon.xml` (sync_version + summary/desc), `ci.yml`, `verify.sh`, README, CONTRIBUTING; regenerated README/reference/web-references blocks; wholesale-bumped ~54 test files; added the 8-doc v2.9.16 evidence set + MANIFEST. **Two pre-existing bugs surfaced + fixed during verification:** (a) `discovery._safe_port` mypy `--strict` regression from #329 (`int()` on `object` → behavior-preserving `cast(Any, …)`; gate back to 51/0); (b) **AutoScript CR/LF injection** — `autoscript_helper.generate()` embedded path/cred fields raw, so a `\r` corrupted the generated `autoexec.sh` (found by the #330 property test, which is non-deterministic AND `hypothesis` isn't a CI dep, so CI never caught it). Operator chose **"full cross-area fix"**: new `_safe_text` in `generate()` + the byte-exact `autoscript-gen.ts` mirror's `safeText` + a new `crlf_paths` fixture + both consistency guards green. **Two commits on `release/v2.9.16`:** `b2d83b2` (hardening: AutoScript CR/LF + `_safe_port` typing) + `e356020` (release bump + evidence). **NOT merged/tagged/published** (EOD called before the merge step). **Resume (addon) — FIRST, finish the v2.9.16 ship:** `gh pr merge 333 --merge --delete-branch` → `git tag -a v2.9.16 origin/main -m "…"` + push (→ `package.yml` publishes the GitHub release + ZIP/SHA256) → `gh release edit v2.9.16 --title "v2.9.16 Final" --notes-file …` → SHA-comment the folded issues (do **NOT** close) → add the Phase-C row to `docs/MANUAL_VERIFICATION_CHECKLIST.md` → refresh `docs/ai-handoff/AI_RESUME_GUIDE.md`. THEN Phase-C the merged backlog on hardware; or the teaching-commentary pass (§3c, paused, awaiting Step-2 sign-off).

---

**As of 2026-06-03 (EOD #19 — add-on `int()` coercion fixes via a property-test pass; bundled into configurator v0.9.4).**
**Clean stopping point — no add-on release cut (the configurator bundles `main`'s add-on, still **v2.9.15**); `main`@`7c9d1d8`; 0 open PRs; add-on suite 1187/3 (serial coverage 99%, ruff clean).**
The configurator "Do 1 2 3" session's only add-on change: a **property-test pass** ([#330](https://github.com/skull-01/script.oppo203.iso.external/pull/330) — `tests/test_property_addon_robustness.py`, Hypothesis-or-curated-fallback) over the discovery + autoscript pure helpers, which **caught + fixed 4 `int()`-coercion crashes** (bug [#329](https://github.com/skull-01/script.oppo203.iso.external/issues/329)): a textual (`"8060/tcp"`) or non-finite (`inf`) port from device-cache JSON / an mDNS record / a JSON AutoScript preset raised `ValueError`/`OverflowError` instead of degrading. Fix: new `discovery._safe_port` (routed through `parse_mdns_record`/`DeviceCache.add`/`.load`) + `autoscript_helper._safe_int` now catches `OverflowError`. **Same class as the EOD #14 `http_info_indicates_playing` fix.** #329 SHA-commented + **OPEN**. **No separate add-on release** — the fix ships inside **configurator v0.9.4** (CI repackages `main`'s add-on). **Resume (addon):** unchanged — Phase-C the merged backlog on real hardware; or the teaching-commentary pass (§3c, paused, awaiting Step-2 sign-off). _A future add-on release (v2.9.16) should fold in #329's fixes on the add-on track._

---

**As of 2026-06-03 (EOD #14 — one defensive add-on fix during the configurator session; addon clean).**
**Clean stopping point — no addon work in flight; `main`@`eec9edf`; 0 open PRs; addon suite 1158/3 (serial coverage 99%, mypy --strict 51/0, ruff clean).**
The configurator-driven session's only add-on change: a **property-test pass** ([#276](https://github.com/skull-01/script.oppo203.iso.external/pull/276) — `tests/test_property_http_hdmi.py`, Hypothesis-or-fallback) over the Xnoppo V3 HTTP/SVM3 predicates + HDMI helpers, which **caught + fixed a real `OverflowError`** in `http_info_indicates_playing` (`int(float('inf'))` was guarded only by `except (TypeError, ValueError)`) — broadened to include `OverflowError` (issue [#275](https://github.com/skull-01/script.oppo203.iso.external/issues/275), SHA-commented + OPEN; same class as the v1.1.9 `i18n.L(inf)` fix). **No separate add-on release** — the configurator bundles `main`'s add-on, which stays **v2.9.15**; the fix ships inside configurator v0.8.6+. **Resume (addon):** unchanged — Phase-C the merged Pure-HTTP / SVM3 / robustness backlog on real hardware; or the teaching-commentary pass (§3c, paused, awaiting Step-2 sign-off).

---

**As of 2026-06-03 (EOD #12 — full-audit remediation: ALL addon findings fixed + merged).**
**Clean stopping point — no addon work in flight; `main`@`49972f5`; 0 open PRs; working tree clean (addon suite 1155/3).**
The operator ran a **full audit** (7 read-only agents over addon + configurator); the addon-area findings were
remediated across **5 PRs merged to `main`**: **A1** [#225] (H1 AVR `http_handoff` eligibility — AVR power-on/input/
restore were silently skipped under the Pure-HTTP default; M1 OPPO HTTP translate-before-BDMV + anchored prefix
rewrite; M10 AVR power-on settle delay; L4 URL-encode backslash), **A2** [#234] (H4 SVM3 startup-timeout gated on
confirmed-playback not device chatter; M2 single-`recv` buffering in `oppo_control` + eISCP; M5 ADB live-test dict→
Settings; M9 clone-wake package-relative import; L1 LOADING≠confirmed; L2 fall-back snapshot; L10 verbose_push;
L13 str.format), **A3** [#238] (M3 declare the 6 emitted keys in `DEFAULTS` + `settings.xml` + an emitted-vs-read
guard; L11 AVR backend-id guard; L15 six→seven comments), **H2** [#255] (`_start_oppo_http` drops the blanket
try/except so a failed `activate→signin→play` is recorded `failed`/rc=1, not silent success), **L12** [#257]
(distinct Samsung `KEY_HDMI1`/`KEY_HDMI2` defaults). ~27 `type:bug` issues filed (#221–#256, area:addon),
SHA-commented + **OPEN** (only-operator-closes); Phase-C rows in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. Gate at
each merge held: pytest **1155/3** · serial coverage 99% · mypy --strict 51/0 · ruff clean. The addon was **not**
separately released (the configurator bundles `main`'s add-on; code stays **v2.9.15**). **Resume (addon): Phase-C
hardware-validate the fixed paths** — AVR firing under the Pure-HTTP default, HTTP path translation, failed-launch
reporting, SVM3 timing — on a real OPPO/AVR/TV. Operator on-device; no agent code. (Only skipped finding: none —
all H/M/L addon items landed.)

---

**As of 2026-06-02 (EOD #11 — Xnoppo V3 / Pure-HTTP SHIPPED; add-on `v2.9.15` released).**
**Clean stopping point — no add-on work in flight; `main`@`be196ac`; 0 open PRs; working tree clean.**
This session built + merged **all 6 Pure-HTTP PRs** and cut **stable add-on `v2.9.15`** (the configurator
bundles it). The add-on slices: **PR1** HTTP/436 primitives ([#208](https://github.com/skull-01/script.oppo203.iso.external/pull/208)),
**PR2** 7th preset `http_handoff_http` + the `http` monitor ([#210](https://github.com/skull-01/script.oppo203.iso.external/pull/210)),
**PR3** pure-HTTP launch orchestration — mount + ISO auto-heal + confirm ([#212](https://github.com/skull-01/script.oppo203.iso.external/pull/212)),
**PR6** checkfolderhasBDMV-first disc nav ([#214](https://github.com/skull-01/script.oppo203.iso.external/pull/214)),
**PR5** `hdmi_sequencing` immediate/delayed ([#218](https://github.com/skull-01/script.oppo203.iso.external/pull/218)).
New add-on modules `resources/lib/oppo/playback_monitor_http.py` + `resources/lib/kodi/hdmi_sequencing.py`;
`oppo_control` gained the HTTP primitives + `resolve_disc_play_path`. **The matrix is now SEVEN presets**
(asymmetric `http_handoff_http`); every new HTTP/mount/BDMV/HDMI step is best-effort + capability-gated so the
six prior presets stay **byte-identical** (build18 order guard green). Gate on the v2.9.15 cut: **pytest 1132/3 ·
serial coverage 99% · mypy --strict 51/0 · ruff clean · audit 598/589→598/598**. ENH **#207/#209/#211/#213/#217**
SHA-commented + **OPEN** (only-operator-closes). **Two gotchas saved to memory:** [[serial-only-monkeypatch-target]]
(a monkeypatch class that passes `-n auto` but fails the serial gate — always run the serial coverage), and
[[xnoppo-v3-pure-http-shipped]] (the 3-place asymmetric preset contract). **Resume (addon): Phase-C hardware-validate
the Pure-HTTP paths** — mount / `getglobalinfo` monitor / ISO auto-heal / checkfolderhasBDMV / `delayed` HDMI timing
on a real OPPO/NAS/TV; scripted in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. Operator on-device; no agent code.

---

**As of 2026-06-02 (EOD #10 — releases shipped; Pure-HTTP build queued as the NEXT THEME).** This session
cut **add-on `v2.9.14`** (six-option playback architecture + SVM3 + richer status + robustness; tag
`v2.9.14`, PR #205 → `a6fdcef`; published via `package.yml`) alongside **configurator `v0.7.0`** (holds the
repo "Latest" badge; bundles the v2.9.14 add-on). No add-on runtime work in flight. **▶ NEXT THEME (queued):
the Pure-HTTP/436 control initiative — PRs 1–6**, fully specified in
[`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) (**Active initiative** section) + decision tree
`build/configurator_decision_tree.html`. It is **cross-area** (add-on + configurator); the add-on slices are
**PR1** (HTTP primitives), **PR3** (mount + HTTP command + auto-heal + HTTP-path BDMV), **PR6** (TCP-path
BDMV), plus the add-on halves of PR2/PR4/PR5. **Resume → pick the Pure-HTTP theme; start Session A = PR1 +
PR2.** (Phase-C hardware validation of the merged SVM3 / http_handoff / guided-install work also still
pending — operator, no agent code.)

---

**As of 2026-06-02 (EOD #9 — no add-on runtime change; one cross-area add-on test added).** This session
was configurator-area (see §3b). The only add-on-area artifact: the cross-area shared-preset guard
**[#203](https://github.com/skull-01/script.oppo203.iso.external/pull/203)** adds
`tests/test_playback_presets_consistency.py`, pinning the add-on's `PLAYBACK_ARCHITECTURE_PRESETS` /
`_PRESET_BY_AXES` / `_ROUTING_ALIASES` (in `resources/lib/kodi/settings_reader.py`) to the new shared
`configurator/src/presets-db/playback-presets.json` — a test-only guard, **no `resources/` runtime change**
(full add-on suite `pytest -n auto` **1053/3** green). A **fullwired audit** this session also confirmed the
add-on reads every configurator-emitted setting (incl. the architecture/preset keys, from the runtime
`settings.xml`). Add-on runtime is otherwise unchanged from EOD #8 below — **Phase-C hardware validation of
the merged SVM3 / http_handoff / robustness / guided-install work is the only remaining add-on work.**

---

**As of 2026-06-02 (this session — Phase 5.1 richer session status MERGED; one add-on change).**
The configurator-track "build Phases 3/4/5" session included **one add-on change** (operator opted into 5.1):
[#183](https://github.com/skull-01/script.oppo203.iso.external/pull/183) `332c0ba` (issue **#182**) enriches
`resources/lib/kodi/playback_session.py`'s `oppo203iso-status.json` with `session_id` (stable per session),
`started_at`/`updated_at`, and a `phase` field (`launching`→`monitoring`→`ended`) + a mid-session heartbeat —
so the live dashboard (Phase 5.2/5.3) can show de-duplicated session telemetry (the identity #166/#168 wanted).
**Backward-compatible** (new optional fields; the configurator's existing `parseOppoStatus` ignores them until
5.2 consumes them). Gate: **pytest 1046/3, mypy --strict 51/0, ruff clean, coverage 99%** (`playback_session.py`
100%). SHA-commented + left OPEN. **Ships on the next configurator build (D-1=C bundles `main` fresh) — no
separate add-on release.** Otherwise the add-on backlog is unchanged from EOD #4 below (Phase-C pending on the
merged SVM3 / http_handoff / robustness work).

---

**As of 2026-06-01 (EOD #6 — guided-install initiative; the add-on side is a release, not new code).**
**Clean stopping point — no add-on runtime change this session; `main` add-on unchanged (1045/3 green).**
The `http_handoff`/SVM3/preset runtime already on `main` (post-2.9.13) was **built + published as a
pre-release `v2.9.14-experimental`** (annotated tag off `main`, no merge) so the configurator can bundle a
working add-on — **no `resources/` change**. The add-on *code* the initiative wants is **deferred**: Phase
2.3 (a configurator-handshake marker) is already satisfied by `architecture_choice_made`, and a new add-on
setting needs operator sign-off; Phase 5.1 (richer live status in `playback_session.py`) is paused pending
hardware. **Resume (add-on):** unchanged from EOD #4 below — Phase-C the merged SVM3 / http_handoff /
robustness backlog on real hardware.

---

**As of 2026-06-01 (EOD #4 — audit stack MERGED; "Merge all").** **Clean stopping point — no addon
work in flight; `main`@`9b0cb6d`; 0 open PRs.** The operator picked **addon Phase C** (operator
hardware; no agent code) + configurator theme 1, then directed **"Merge all".** The addon **issue-audit
stack MERGED** to `main` — **docs-only** (empty `resources/` diff, so the addon suite is unaffected and
stays **1045/3**):
[#161](https://github.com/skull-01/script.oppo203.iso.external/pull/161) `fdd3368` (robustness audit) →
[#162](https://github.com/skull-01/script.oppo203.iso.external/pull/162) `a543615` (SVM3 + verify-played
audit) → [#163](https://github.com/skull-01/script.oppo203.iso.external/pull/163) `e957aab` (cross-links
+ `docs/audit/README.md`). Merged bottom-up cleanly by **retargeting the stacked children to `main`
first** (the corrected stacked-merge procedure — see §3b lessons). So the per-issue **Phase-C runbook now
lives on `main` under [`docs/audit/`](docs/audit/README.md)**: #111/#112/#114–#117/#123 robustness +
#150/#151/#152 SVM3 all confirmed-fixed at a `file:line` + pinning test; **#113 partial** (svm3 confirms
playback; the legacy hold path is start-confirmation-free *by design* — operator decides disposition at
Phase C). The merged-code state (SVM3 #143–#145, http_handoff #154–#157) is unchanged from EOD #2 below.

**Resume here next (addon), pick one (per §4):**
1. **Phase-C the whole addon backlog on real hardware** — now fully scripted in `docs/audit/` + the
   checklist (SVM3 `#QVM`/`#SVM 3`/`@UPL`/`@UTC`; http_handoff NAS launch + `oppo_http_path_*`
   translation; the robustness judgment constants); close the issues. Operator on-device; no agent code.
2. **Decide #113's disposition** — close as satisfied-by-SVM3, or keep it open scoped to the legacy path.
3. **Teaching-commentary pass** (§3c, PAUSED) — rebase the wip branch first; awaiting Step-2 sign-off.

---

**As of 2026-06-01 (EOD #3 — addon issue audit, docs only).** **Clean stopping point — no addon
CODE in flight; `main`@`72c84d8` (code unchanged); 3 new draft PRs.** This session was a
**pure-agent audit** of the open addon backlog (no runtime change), delivered as 3 stacked draft PRs:

- **[#161](https://github.com/skull-01/script.oppo203.iso.external/pull/161)** robustness audit —
  #111/#112/#114/#115/#116/#117/#123, each **confirmed fixed in code** at a cited `file:line` + a
  passing pinning test (`docs/audit/addon_robustness_audit.md`).
- **[#162](https://github.com/skull-01/script.oppo203.iso.external/pull/162)** SVM3 + verify-played
  audit — #150/#151/#152 confirmed fixed; **#113 is partial** — fully realized for the SVM3 monitor
  (`confirmed_playback`/`confirmed_progress` from real `@UPL`/`@UTC`), but the **legacy** hold path is
  start-confirmation-free *by design*. Audit recommends closing #113 as satisfied-by-SVM3 with a note,
  or keeping it open scoped to the legacy path — **operator decides at Phase C**
  (`docs/audit/addon_svm3_audit.md`).
- **[#163](https://github.com/skull-01/script.oppo203.iso.external/pull/163)** cross-links +
  `docs/audit/README.md` + a single pointer block at the top of `MANUAL_VERIFICATION_CHECKLIST.md`.

The per-issue **Phase-C steps live in `docs/audit/`**, so the hardware session is a checklist, not a
re-investigation. Verified: **docs only** (empty `resources/` diff), cited tests re-run **24 + 69 =
93 passing**, `ruff format --check` clean, full addon suite on `main` **1045/3**. **No addon code
changed** — the merged-code state (SVM3 + http_handoff) is unchanged from the EOD #2 block below;
Phase C still pending on the whole backlog.

**Resume here next (addon), pick one (per §4):**
1. **Review + merge the audit stack** [#161](https://github.com/skull-01/script.oppo203.iso.external/pull/161) → [#162](https://github.com/skull-01/script.oppo203.iso.external/pull/162) → [#163](https://github.com/skull-01/script.oppo203.iso.external/pull/163) (bottom-up), then run `docs/audit/` at the hardware for Phase C and close the backlog; decide #113's disposition.
2. **Phase-C the merged SVM3 + http_handoff** on real hardware (operator; no agent code) — now scripted in `docs/audit/`.
3. **Teaching-commentary pass** (§3c, PAUSED) — rebase the wip branch first; awaiting Step-2 sign-off.

---

**As of 2026-06-01 (EOD #2 — SVM3 stack merged + http_handoff six-option, addon side).** **Clean
stopping point — no addon work in flight; `main`@`72c84d8`; all addon PRs merged + pushed.** This
session **merged** the SVM3 four-option stack AND added **`http_handoff` as a sixth playback option**:

- **SVM3 stack MERGED** — #143 `fadd8c9` (`playback_monitor_mode` reader), #144 `ccf3638`
  (`OppoSvm3PlaybackMonitor`), #145 `421c2f0` (shared `run_playback_session`). **ENH issues filed:**
  [#150](https://github.com/skull-01/script.oppo203.iso.external/issues/150) /
  [#151](https://github.com/skull-01/script.oppo203.iso.external/issues/151) (relates #113) /
  [#152](https://github.com/skull-01/script.oppo203.iso.external/issues/152) — SHA-commented, awaiting
  operator Phase-C + close. (#144/#145 show *Closed* not *Merged* — stacked-local-merge artifact, code
  is on `main`; see memory `stacked-pr-local-merge-status`.)
- **`http_handoff` six-option MERGED** — #154 `b630b85` (routing 2→3 + the 2 new presets
  `http_handoff_legacy`/`http_handoff_svm3`, reader-only) + #155 `87fbfc6`
  (`external_player.fast_start_http` + `run_playback_session` routing branch; **reuses** the existing
  `oppo_control` HTTP fns — no refactor). The 4 existing presets are frozen + regression-pinned; the
  legacy/svm3 monitor axis is untouched (confirmation falls out of it). HTTP-launch failure is non-fatal.

Gate on `main`@`72c84d8`: pytest **1045/3**, coverage **99%**, ruff + mypy `--strict` **51/0**.
**Phase-C on real OPPO/NAS still pending** for SVM3 (#150–#152) + http_handoff + the 7 older
merged-but-open bug fixes (#111/#112/#114–#117/#123) + #113. http_handoff is PR-only (consolidated
checklist row); the OPPO-visible path translation is operator/Phase-C config (the wizard can't know the
player's NAS mount namespace).

**Resume here next (addon), pick one (per §4):**
1. **Phase-C verify** the merged SVM3 + http_handoff work on real hardware (operator; closes #150–#152 + the bug backlog). No agent code.
2. **Teaching-commentary pass** (§3c, PAUSED) — rebase the wip branch first (#145 + #155 both changed `external_player.py`); awaiting Step-2 sign-off.

**Reference — the SVM3 stack as originally built (now merged), in order #143 → #144 → #145:**

- **[#143](https://github.com/skull-01/script.oppo203.iso.external/pull/143) (`cbae76e`)** — adds the
  monitor axis `playback_monitor_mode` (`legacy`|`svm3`, default legacy) + `architecture_preset()` /
  `normalize_architecture()` in `settings_reader.py`. The combined `playback_architecture_preset` is
  configurator-written + source-of-truth, derived from the legacy fields when absent (**no add-on
  default**, so it can't mask a `service_interception` install). Reader-only — mirrors the existing
  `playback_architecture` pattern (no `settings.xml`/`strings.po` change). `tests/test_architecture_presets.py`
  (18). **No runtime change.**
- **[#144](https://github.com/skull-01/script.oppo203.iso.external/pull/144) (`3b63054`)** — new
  `resources/lib/oppo/playback_monitor_svm3.py` (`OppoSvm3PlaybackMonitor`): a persistent `#SVM 3`
  client extending `oppo_tcp_client` — `#QVM`+restore, `@UPL PLAY`→confirmed_playback, advancing
  `@UTC`→confirmed_progress, bounded ring buffer + summary logging. Code-default tuning (no new
  persistent settings); not yet wired. `tests/test_svm3_playback_monitor.py` (32) → module **100%**.
- **[#145](https://github.com/skull-01/script.oppo203.iso.external/pull/145) (`d5ba5ab`)** — new
  `resources/lib/kodi/playback_session.py` `run_playback_session()`: the single sequence both
  `external_player.main()` and `service._run_interception()` now delegate to; monitor branch =
  legacy (`hold_playback`) | svm3 (the monitor, **falling back to legacy on connect failure**);
  writes a split-truth `oppo203iso-status.json`. `tests/test_playback_session_modes.py` (10).

Each PR's gate was green on its branch (pytest up to **1036 pass / 3 skip**, coverage **99%** — both
new modules 100%, mypy `--strict` 51/0, ruff clean). **Operator to file 3 `area:addon` ENH issues**
(monitor_mode+preset; SVM3 monitor — relates to **#113** verify-played; shared session engine); the
new settings key was authorized in-session. Phase A/C rows for all three are in
`docs/MANUAL_VERIFICATION_CHECKLIST.md`. **Pairs with configurator Session B PRs #146–#149 (§3b)**,
which seed `playback_monitor_mode` + `playback_architecture_preset`. **Heads-up:** #145 rewrote
`external_player.main()`, so the paused teaching-commentary wip branch (comments-only) needs a rebase
before resuming.

**Prior — robustness drafts merged (still the `main` baseline):** the earlier `merge everything`
session merged the 5 robustness draft PRs (#129–#133) to `main`, fixing all 7 open `type:bug` issues;
each is ON `main` but its **issue stays OPEN** awaiting operator Phase-C + close (only-operator-closes):

- **[#129](https://github.com/skull-01/script.oppo203.iso.external/pull/129) (`396634c`)** —
  `hold_playback` bounded holds + verbose_push→`_hold_tcp_qpl_poll` fallback (#112/#115/#116);
  `MAX_CONSECUTIVE_POLL_FAILURES=5`. `tests/test_hold_robustness.py`.
- **[#130](https://github.com/skull-01/script.oppo203.iso.external/pull/130) (`523eadc`)** — default
  `hold_mode`→`tcp_qpl_poll` (#114); `tests/test_hold_default.py`. (Merged after #129, as required.)
- **[#131](https://github.com/skull-01/script.oppo203.iso.external/pull/131) (`29d951f`)** —
  self-healing sentinel `session_is_active()` + `SESSION_MAX_AGE_SECONDS=21600` (#117).
- **[#132](https://github.com/skull-01/script.oppo203.iso.external/pull/132) (`bd0cc42`)** — diag HTTP
  probe `http_port=436` not 80 (#111).
- **[#133](https://github.com/skull-01/script.oppo203.iso.external/pull/133) (`43207ba`)** — `ruff
  format` the 2 drifted test files (#123); **`ruff format --check` on `main` is now clean** (the
  long-standing CI red is gone).

**Merge mechanics (for the record):** the 5 merges all collided on `docs/MANUAL_VERIFICATION_CHECKLIST.md`
(each PR prepended a row at the same anchor) and **#130 was a draft** — resolved by a union-merge of the
checklist (every row kept; aborted on any non-checklist conflict — none) and `gh pr ready` first.
Post-merge `main` green: **pytest 976/3, ruff check + format clean.** **Judgment constants to confirm
on hardware:** the 5-failure abort (#116), the `tcp_qpl_poll` default (#114), the 6h staleness (#117),
the 436 probe (#111).

**Teaching-commentary theme (§3c) still PAUSED, untouched this session** — `wip:` `62b22eb` on
`claude/teaching-comments-extplayer-r3k8m2x9` (pushed, **not** on `main`), awaiting Step-2 style
sign-off. **Heads-up:** #129 (now merged) changed `external_player.py` *logic*; that wip branch
(comments-only) will need a **rebase onto current `main`** before resuming (low conflict — comments
vs logic). Do **not** push/merge it unprompted.

**Candidate themes for next addon session** (pick one, per §4):
1. **Review + merge the SVM3 stack (#143 → #144 → #145)** — review each draft in order and merge
   (or `merge everything` in order); file the 3 ENH issues; then Phase-C the SVM3 modes on real
   hardware (the new checklist rows: `#QVM`/`#SVM 3` accepted, `@UPL`/`@UTC` confirm playback, the
   verbose mode restored on exit). ← resume here.
2. **Phase-C the 7 merged bug fixes (#111/#112/#114/#115/#116/#117/#123)** + **#113 verify-played**
   (SVM3 is now its richer realization) — operator on-device steps; close the issues. No agent code.
3. **Teaching-commentary pass (cross-area, PAUSED — awaiting Step-2 sign-off)** — reproduce §3c's
   verbatim briefing EXACTLY when proposing (operator directive); **rebase the wip branch first**
   (#145 changed `external_player.main()`).

---

**Prior session — 2026-05-31 (EOD — naming-consistency + draft-merge).** **Clean stopping point —
no uncommitted addon work; all addon PRs merged to `main` (HEAD `8c35f28`); 0 open PRs.** This
session **merged the two prior-session addon drafts and renamed the TV backend modules:**

- **Read-only OPPO status probe — MERGED** ([PR #118](https://github.com/skull-01/script.oppo203.iso.external/pull/118), merge `8c35f28`; resolved a docs-only
  checklist conflict on merge). `oppo_control.probe_player_status()` fires the documented `#Q..`
  battery over TCP:23 + a "Probe OPPO player status (diagnostic)" installer menu action;
  `docs/OPPO_PROTOCOL_REFERENCE.md`; `tests/test_oppo_status_probe.py` (13 tests). Landed **ahead
  of hardware verification** (operator chose to merge). **No change to routing / payloads / hold
  modes.** ← **Operator's next step (Phase C in the checklist):** run the probe on the real Kodi
  box + OPPO and paste `oppo-status-probe.txt` — does a NAS-ISO handoff report the ISO name via
  **`#QFN`** (or mount as a disc → `#QDT`)? That answers + unblocks the **#113**
  `verify_playback_started()` follow-up wired into `fast_start`.
- **Addon functional-flow diagrams — MERGED** ([PR #119](https://github.com/skull-01/script.oppo203.iso.external/pull/119), merge `1a22c06`):
  `docs/ADDON_FUNCTIONAL_FLOW.md` (Mermaid diagrams + findings appendix).
- **TV backend modules renamed `tv_*` — MERGED** ([PR #126](https://github.com/skull-01/script.oppo203.iso.external/pull/126)): `adb_control`→`tv_adb_control`,
  `roku_ecp_control`→`tv_roku_ecp_control`, `smartthings_control`→`tv_smartthings_control` (parity
  with the `avr_` drivers — a file "about TV" now carries `tv_`). Updated the alias-finder
  `_BUCKET` map, `mypy.ini`, `pyproject.toml`, `tests/_support/lib_buckets.py`, the
  `tv_control`/`tv_diagnostics` imports, and 6 tests; **module bodies unchanged.** Gate green
  (pytest 963, coverage 99%, ruff/mypy clean). Naming rationale + the OPPO↔player role/brand
  duality now in **`docs/NAMING_CONVENTIONS.md`** ([PR #128](https://github.com/skull-01/script.oppo203.iso.external/pull/128)); historical build-note refs flagged
  (not rewritten).
- **Filed `type:bug` [#123](https://github.com/skull-01/script.oppo203.iso.external/issues/123)** — pre-existing `ruff format --check` drift on 3 test files
  (`test_all.py`, `test_players_db_consistency.py`, `test_v2910_build2_player_taxonomy.py`); the
  **only** red on CI "Lint and format", unrelated to the renames (which added no new drift). A
  spawn-task chip was queued to fix it (one `ruff format` run + full-suite re-verify).
- **Robustness issues from the prior review remain OPEN, not yet implemented:** **#111** (port-80
  diag probe), **#112** (verbose_push→fixed_timeout degrade), **#113** (*ENH* verify-played, now
  with the merged probe as its precursor), **#114** (blind 180-min default hold), **#115**
  (`manual_file` infinite), **#116** (polling 240-min on OPPO loss), **#117** (stale sentinel). Plus
  standing **#44** (hardware-validation solicitation).

**Teaching-commentary theme (§3c) is still PAUSED, untouched this session** — `external_player.py`
commented, `wip:` `62b22eb` on `claude/teaching-comments-extplayer-r3k8m2x9` (pushed, **not** on
`main`), still awaiting the operator's Step-2 *style sign-off*. The verbose_push degrade it noted is
now filed as **#112** (+ the blind-default-hold issue **#114**). Do **not** push/merge that wip
branch unprompted.

**Prior context (durable) — recent addon-area changes:**

- **Players-DB consistency guard (test-only, merged 2026-05-30)** — the TV-DB-v2 / players-DB
  session ([PR #106](https://github.com/skull-01/script.oppo203.iso.external/pull/106), merge `81c3eb5`) added `tests/test_players_db_consistency.py` (pins the new
  configurator `players.json` to the live `hardware_profiles` / `HARDWARE_COMPAT` / capability
  tuples / `settings.xml` enum order / aliases) and made the two `len(HARDWARE_COMPAT) == 18` count
  guards derive from the DB. **No add-on runtime change** — the add-on doesn't load `players.json`
  at runtime (same split as the TV DB). See [[oppo-hardware-model-taxonomy-map]] + §3b. Done, not in flight.

**2026-05-30 evening merge/release session — the addon-area deliverable was:**

- **Chinoppo `M9205 V1` split into a distinct hardware model** ([PR #91](https://github.com/skull-01/script.oppo203.iso.external/pull/91), merge `36f9cbd`): new `oppo_hardware_model` enum value `chinoppo_m9205_v1`, **appended** to `resources/settings.xml` (existing stored enum indices preserved) and mirrored through `settings_reader` / `hardware_profiles` / `hardware_capabilities` as an **exact `M9205` clone** (`#EJT` eject-to-wake, clone-safe, `http_api_436=False`); configurator `players.ts` re-pointed (plain `M9205` still → `chinoppo_m9205`); taxonomy count guards 17→18; new `tests/test_chinoppo_m9205_v1_split.py` (5 tests). Additive — **no behavior change to existing models.** PR-only (no tracked issue); Phase-A/C entry in the manual checklist. **Software-verified only** — the V1 mirror assumes identical protocol per the operator's confirmation; if real hardware shows it differs, its `HARDWARE_COMPAT` / profile entries need distinct values.

- **ENH-#51 mypy `--strict` rollout — COMPLETE and now CLOSED by the operator** (gate **49/0**; every `resources/lib` module + top-level `service.py`/`default.py` gated; CI `types` job enforces it). Nothing to resume. The full PR-by-PR history is in §15; recipe + all idioms (the no-redef strategy, `Settings.get -> Any`, conditional-Kodi-base `# type: ignore[misc]`, `X | None` over `Optional` for ruff `UP045`, the parallel-sub-agent technique) are in memory `mypy-strict-gate-rollout`.

- **Backlog cleared (2026-05-30 EOD).** The operator closed the five delivered addon issues
  — #38 (ruff), #41 (config-owner Parts A/B/C), #42 (settings menu), #43 (lib split), #57
  (fast test loop) — plus the 16 configurator review bugs (#72–#87) and #51, **ahead of
  hardware testing**, and will re-file whatever's still outstanding after on-device
  verification (the Phase A/C steps in `docs/MANUAL_VERIFICATION_CHECKLIST.md` still apply).
  The only addon issue left open is **#44** (hardware-validation solicitation — a standing
  community call for tester reports / lending / donations).

- **Candidate themes (this prior session's list)** — **superseded.** This session's robustness
  bug-fixes (#114/#115/#116/#117/#111/#112) and the #123 ruff-format fix were all delivered as draft
  PRs #129–#133; see the **current** candidate themes at the top of §3a.

## §3b Configurator — archived entries

**As of 2026-06-03 (EOD #20 — configurator touched ONLY by the v2.9.16 release's cross-area AutoScript mirror fix; cfg themes 1 & 2 grounded but NOT started).**
**Stopping point: no standalone configurator release this session; the AutoScript-gen TS mirror change rides inside add-on PR [#333](https://github.com/skull-01/script.oppo203.iso.external/pull/333) (`release/v2.9.16`); `main`@`5fa1b70`; **configurator-v0.9.4 still holds the repo "Latest".**
The operator's 3-theme override included **Cfg theme 1 (i18n migration)** and **Cfg theme 2 (installer single old-version prompt)**, but the session went to the add-on v2.9.16 release (§3a) and hit `done for the day` first. The **only** configurator change this session: `configurator/src/autoscript/autoscript-gen.ts` gained `safeText` (strip CR/LF) to stay byte-identical to the add-on's hardened `generate()`, plus a `crlf_paths` fixture (`autoscript-fixtures.json`) and the matching `autoscript.test.ts` case — cfg gate green (`tsc -b`, **vitest 357**, `vite build`). This ships **inside add-on PR #333** — **no configurator version bump, no new configurator release** (the next `configurator-v*` tag will bundle the v2.9.16 add-on once #333 merges). **Resume (configurator) — both themes still QUEUED (grounded this session, turnkey):**
- **Theme 1 — i18n migration.** PR #277's `i18n.ts` `t()` scaffold has only `WinShell` migrated; **~660 raw strings across ~32 files** remain. Grounded 4-PR slice: (1) catalog **no-missing/no-orphan guard** + shared chrome (`FooterNav`/`Progress`/`Sidebar`/`Chain`/`App.tsx`/`steps.ts` label text) + fix `App.tsx:142` raw-title override; (2) Step 0 cluster + `step1.tsx`; (3) `step2`–`step6.tsx`; (4) `test.tsx`/`dashboard.tsx` + 7 dev panels. Hazards: `t()` has only `{name}` interpolation (no pluralization / no rich-text — split around inline `<em>`/`<strong>`); keep wizard order/numbers authoritative in `steps.ts` (`steps.test.ts` pins wiring, not label text); dynamic label maps in `dashboard.tsx`/`test.tsx` need `{var}` keys.
- **Theme 2 — installer single old-version prompt.** Suppress Tauri's built-in NSIS reinstall page via a **vendored template**. FEASIBLE but the template ships only embedded in the CLI napi binary (cli **2.11.2**) — vendor by fetching GitHub tag `tauri-cli-v2.11.2` (diffable) or binary-carving; then remove `PageReinstall`/`PageReinstallUpdateSelection`/`PageLeaveReinstall` (~202 lines), broaden `installer-hooks.nsh`'s `NSIS_HOOK_PREINSTALL` to also detect+remove a prior **NSIS** install (it currently delegates that to the page), and set `nsis.template` in `tauri.conf.json:44`. Behavior is **host/Phase-C-only** verifiable (config-parse + `makensis` compile in-session); ship needs a new `configurator-v*` tag. Consider a CI guard that the vendored template matches the CLI version (drift risk).

---

**As of 2026-06-03 (EOD #19 — quality + capability roll-up SHIPPED; cut configurator v0.9.4 via the CI tag).**
**Clean stopping point — 0 open PRs; `main`@`7c9d1d8` is configurator v0.9.4; all three changes merged + CI-gated; release built + published by the CI tag job.**
Operator: "What else can we do" → **"Do 1 2 3 then 4"** — (1) review the session's code + fix findings, (2) add-on property-test pass, (3) AVR raw-command console, (4) wrap up. All three built + merged:
- **(1) Dev-console hardening** [#328, cfg] — an independent adversarial review of the session's ~21 PRs found **no high/blocking issues**; applied its medium+low findings: `nas_test_smb` rejects net.exe-confusing creds (quotes/newlines, or a `/`-leading / `*` password it reads as a switch/prompt), `autoscript_push_telnet` rejects a line == the heredoc terminator (`OPPOEOF`), `validate_addon_zip` caps each entry's decompressed read at 16 MB, `install_addon_zip` rejects quotes/newlines in the addons path, and the Kodi panel relabels "signed build" → **"build tag verified"** (content-integrity, not crypto). **No issue** (review fixes).
- **(2) Add-on property-test pass** [#330, **area:addon**; bug #329] — a property/fuzz sweep over the add-on's pure helpers found + fixed a cluster of `int()`-coercion crashes: a textual (`"8060/tcp"`) or non-finite (`inf`) port from device-cache JSON / an mDNS record / a JSON AutoScript preset raised `ValueError`/`OverflowError` instead of degrading. Fix: new `discovery._safe_port` (routed through `parse_mdns_record`/`DeviceCache.add`/`.load`) + `autoscript_helper._safe_int` now catches `OverflowError`. New `tests/test_property_addon_robustness.py` (optional Hypothesis + curated fallback) pins the 4 fixes + the eISCP round-trip + path-normalize idempotence. **Rides into the bundled add-on.** Same root cause as the EOD #14 `OverflowError` fix.
- **(3) AVR raw-command console** [#332, cfg; ENH #331] — the dev panel's AVR tab gains a raw-command console (arbitrary power/volume/mute/query) alongside input-select, via a new thin Rust **`avr_raw_send`**: Denon line-ASCII over telnet (:23), Onkyo/Pioneer eISCP framed over :60128, Yamaha MusicCast path over HTTP (:80); Sony keeps its `setPlayContent` URI box. Pure builders (`denon_raw_command`/`eiscp_raw_payload`/`yamaha_raw_path`) reject control chars / over-length / traversal / header-splitting before any socket opens. Render-verified in the preview (Denon + eISCP palettes, placeholders, hints).
Then bump → tag **`configurator-v0.9.4`** → CI repackages `main`'s add-on (now carrying #330's fixes) + publishes as Latest. Gates: `tsc -b` · **vitest 356** · **cargo 57** · `vite build`; add-on **pytest -n auto 1187/3** · **serial coverage 99%** · ruff clean. Bug **#329** + ENH **#331** SHA-commented + **OPEN**; #328 is review fixes (no issue); Phase-C rows in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. New Rust cmd: `avr_raw_send`. **Resume (configurator):** Phase-C the AVR raw commands on a real receiver + the add-on cache/mDNS recovery on-device, or a fresh theme.

---

**As of 2026-06-03 (EOD #18 — embedded add-on build tag SHIPPED; cut configurator v0.9.3 via the CI tag).**
**Clean stopping point — 0 open PRs; `main`@`6266aa7` is configurator v0.9.3; both build-tag PRs merged + CI-gated; release built + published by the CI tag job.**
Cross-area follow-up to the v0.9.2 add-on validation (the operator chose the deferred "embedded tag", umbrella **[#322]**): full content hash · allow-unsigned-but-label.
- **PR 1** [#325, **area:addon**] — `tools/package_installable_zip.py` stamps `resources/oppokodiaddon.sig` (addon id/version + a SHA-256 content manifest over the zip's files, via `compute_manifest_sig`) into the installable zip — Kodi-inert metadata under the allowlisted resources/ dir, **no runtime change**; the allowlist invariant (`set(namelist)==names`) holds. Gate: pytest -n auto **1162/3**, **serial coverage 99%**, ruff clean.
- **PR 2** [#326, cfg] — `validate_addon_zip` recomputes the manifest (Rust `addon_manifest_sig` + dep `sha2`) → **signed** / **unsigned** (older build, still allowed + labeled) / **mismatch** (tampered → blocked). KodiPanel shows the state on the validation line.
**Cross-language guard:** a cargo test pins `addon_manifest_sig` to the **same fixture hash** as `tests/test_addon_signature.py` (`bbcc6382…`) — Python (packaging) ↔ Rust (validation) can't drift. Then bump [#327] → tag **`configurator-v0.9.3`** → CI repackages `main`'s add-on (now signed) + publishes as Latest. Gates: `tsc -b` · vitest 356 · **cargo 54** · `vite build`. ENH **#323/#324** (+ umbrella **#322**) SHA-commented + **OPEN**; Phase-C rows in the checklist. **Resume (configurator):** Phase-C the dev-console + AutoScript + build-tag flows on real hardware, or a fresh theme.

---

**As of 2026-06-03 (EOD #17 — Developer Options UX refinements SHIPPED; cut configurator v0.9.2 via the CI tag).**
**Clean stopping point — 0 open PRs; `main`@`07a3f3f` is configurator v0.9.2; all 3 refinement PRs merged + CI-gated; release built + published by the CI tag job.**
Operator feedback after the AutoScript ship → 3 refinements (umbrella **[#314]**), answered the one open decision (add-on validation = identity+structure, not crypto), built + merged:
- **PR 1** [#318] **side-by-side live transcript** — new responsive `.dev-split` layout (controls left, transcript in a tall sticky right column, collapses to 1 col under 900px) on the OPPO/TV/AVR/NAS/AutoScript panels, so the live screen sits beside the controls instead of stacked at the bottom.
- **PR 2** [#319] **Browse + add-on validation** (Kodi upload) — a native file picker (new Rust `pick_addon_zip` via the `rfd` crate) + `validate_addon_zip` → {valid, version, reason} (identity+structure: our addon id, default.py/service.py/resources/lib, parseable version; pure `validate_addon_contents` cargo-tested). Upload + register stays disabled until a valid OppoKodiAddon zip is picked; reason shown inline. Identity check, not cryptographic (unsigned posture).
- **PR 3** [#320] **TV HDMI input switch** — an "HDMI input switching" card atop the TV console: Switch to OPPO / Switch to Kodi fire the wizard's configured switch via `planSwitch` (the exact add-on handoff), with an honest manual fallback; plus ADB HDMI presets.
Then bump [#321] → tag **`configurator-v0.9.2`** → CI built MSI/NSIS + published as Latest (bundles add-on **v2.9.15**). Gates green: `tsc -b` · **vitest 356** · **cargo test 53** (+`rfd`) · `vite build`; browser-verified the 2-col layout, the Upload-disabled-until-valid gate, the HDMI switch wiring. New Rust cmds: `validate_addon_zip`, `pick_addon_zip`. New dep: `rfd`. ENH **#315–#317** (+ umbrella **#314**) SHA-commented + **OPEN**; Phase-C rows in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. **Resume (configurator):** Phase-C the AutoScript flow + these refinements on real hardware, or a fresh theme.

---

**As of 2026-06-03 (EOD #16 — AutoScript helper SHIPPED as the 6th Developer Options sub-section; cut configurator v0.9.1 via the CI tag).**
**Clean stopping point — 0 open PRs; `main`@`02f44bf` is configurator v0.9.1; all 3 AutoScript PRs merged + CI-gated; release built + published by the CI tag job.**
Operator (right after the Developer Options release): "add another section on the dev panel — autoscript, everything here to check and install autoscript to a JB and clone OPPO; create a plan." Produced a canonical plan; operator answered the open inputs (export a **Desktop folder** the user copies to USB with an instructions file · keep **telnet** push + availability check · release **v0.9.1**) = Go. Built **3 PRs** under umbrella **[#306]**:
- **PR 1** [#310] generator + capability **contract** — `configurator/src/autoscript/autoscript-gen.ts` is a byte-exact mirror of the add-on's `autoscript_helper.generate()` (autoexec.sh: telnet/2323, passwordless root, NFS/CIFS mount, ADB, heartbeat); `capability.ts` mirrors `oppo20x_autoscript_firmware_status` (20X-56 min / 20X-65-0131 rec) + JB/clone family. Cross-language guard `tests/test_autoscript_consistency.py` (add-on side) + `autoscript.test.ts` (cfg side) both pin to `autoscript-fixtures.json`. No UI/IO.
- **PR 2** [#311] panel — 6th DevTab "AutoScript": builder form → live `autoexec.sh` preview → readiness check (`#QVR` firmware capability + family + telnet/ADB/HTTP probes + port-23 risk callout) → **export `<Desktop>/OppoKodiAddon-AutoScript/`** (autoexec.sh + HOW-TO-INSTALL.txt: FAT32 / copy to USB root / boot / verify) via new Rust `export_autoscript_bundle`. New `readme.ts` + `parseQvrFirmware`. CIFS password shown in the preview, never persisted.
- **PR 3** [#312] telnet — `autoscript_telnet_check` (probe busybox telnetd :2323 for a live shell) + confirm-gated `autoscript_push_telnet` (push autoexec.sh via a quoted heredoc + chmod). USB export stays primary for a fresh player.
Then bump [#313] → tag **`configurator-v0.9.1`** → the CI release job builds MSI/NSIS + publishes as Latest (bundles add-on **v2.9.15**). Gates green: `tsc -b` · **vitest 356** · **cargo test 51** · `vite build`; add-on `pytest -n auto` **1160/3** + serial coverage **99%** + ruff clean (PR 1's cross-language guard). Every panel browser-verified (live preview updates, port-23 toggle, the redaction, the confirm gates). ENH **#307–#309** (+ umbrella **#306**) SHA-commented + **OPEN**; Phase-C rows in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. New Rust cmds: `export_autoscript_bundle`, `autoscript_telnet_check`, `autoscript_push_telnet`. **Resume (configurator) — Phase-C** the AutoScript flow on a real JB/clone OPPO (USB boot of autoexec.sh, the #QVR/port readiness, telnet check + push), then pick a fresh theme.

---

**As of 2026-06-03 (EOD #15 — Developer Options console SHIPPED across 7 PRs; cut configurator v0.9.0 via the CI tag).**
**Clean stopping point — 0 open PRs; `main`@`c3b8bcf` is configurator v0.9.0; all 7 PRs merged + CI-gated; release built + published by the CI tag job.**
Operator picked `resume` → Configurator → the LOCKED **Developer Options** theme, then "complete all the phases automatically then release it" (full auth, 4 up-front decisions: v0.9.0 via CI tag · documented OPPO TCP set + raw box · umbrella + per-PR ENH issues · merge-as-I-go). Built + merged **all 7 PRs** under umbrella **[#290]**, each CI-gated and merged to `main` as it passed:
- **PR A** [#298] dev-tab shell + nav — a `developer` screen + a persistent header "Developer…" entry (hidden on dev screens, mirrors #264 reset-all), 5 sub-section tabs, wired into `steps.ts` (ScreenId + both maps) + `App.tsx`, pinned by `steps.test.ts`.
- **PR B-OPPO** [#299] OPPO console — TCP palette (canonical 76-key `#XXX` map → `oppo-commands/tcp-commands.ts`) via `oppo_query` + raw box; HTTP palette over the 61-endpoint catalog (#285) via a new generic `oppo_http_get`; live transcript with a TCP-push (`#SVM 3`) ⇄ HTTP-poll (`getmovieplayinfo`+`getglobalinfo`) monitor switch. Credential endpoints redacted in the transcript + never persisted (`oppoConsole.ts`, unit-tested).
- **PR C** [#300] Kodi dev tools — installed-vs-bundled version (`bundled_addon_info` + box `addon.xml` over SSH), a live settings table, register-without-restart (`kodi_set_addon_enabled`), remote restart (new `kodi_restart`), upload-any-version (new `install_addon_zip`); restart + zip-upload confirm-gated.
- **PR D-TV** [#301] TV console — all backends (Roku ECP / ADB / Sony Bravia / LG-Samsung-custom / SmartThings), each fired via the existing `tv_switch_*`/`smartthings_switch_request` + a new generic IRCC `tv_sony_bravia_ircc`; shared live transcript (new `devTranscript.tsx`: `useTranscript`/`Transcript`/`runAndLog`).
- **PR D-AVR** [#302] AVR console — all backends via the existing `avr_switch_*` (input-select; **0 new Rust cmds**); shared form controls (`devControls.tsx`).
- **PR D-NAS** [#303] NAS panel — `scan_nas_hosts` (parallel /24 sweep of 445/139/2049/548/21 + protocol-detect) + `nas_test_login` (SMB net-use auth+list / NFS reachability); creds redacted + never persisted; shared subnet sweep helpers (`local_ipv4`/`subnet_hosts`/`parallel_open_ports`).
- **PR E** [#304] Kodi LAN scan — `scan_kodi_hosts` (:8080 sweep + JSON-RPC `Application.GetProperties` confirm, yields version), lists found boxes + fills the Kodi IP; reuses the D-NAS subnet helpers.
Then bump [#305] → tag **`configurator-v0.9.0`** → the **CI release job** builds MSI/NSIS + publishes as Latest (bundles add-on **v2.9.15**). Gates green throughout: `tsc -b` · **vitest 338** · **cargo test 50** · `vite build`; every panel **browser-verified** (nav, command-firing, the OPPO + NAS credential redaction, the Kodi scan). ENH **#291–#297** (+ umbrella **#290**) SHA-commented + **OPEN** (only-operator-closes); Phase-C rows in `docs/MANUAL_VERIFICATION_CHECKLIST.md`; `docs/BUILD_PLAN.md` §2 is now **✅ DELIVERED**. **Resume (configurator) — Phase-C** the whole Developer Options surface on real OPPO/Kodi/TV/AVR/NAS (every console's device I/O is hardware-pending: TCP/HTTP commands, verbose-push/HTTP monitors, SSH register/restart/zip-upload, the scans, the SMB/NFS login), then pick a fresh theme. Standing rule: a bare "release" = the configurator release bundling the add-on (see [[configurator-release-is-manual]], CI path).

---

**As of 2026-06-03 (EOD #14 — 7-theme infra/hardening batch + configurator v0.8.6 cut by the NEW CI release automation).**
**Clean stopping point — 0 open PRs; `main`@`2eaf1a7` is configurator v0.8.6 (the docs-wrap commit follows); the configurator gate now runs in GitHub Actions.**
Operator: "do all of this automatically" — seven themes, each delivered as its own CI-gated PR:
- **[#271](https://github.com/skull-01/script.oppo203.iso.external/pull/271)** repo hygiene — `.gitignore` the local scratch (reconstruction MDs, `.claude/launch.json`/`worktrees`); fixed the stale `audit_release --expected-version 2.9.10`→`2.9.15` in README + CONTRIBUTING; `git prune`.
- **[#272](https://github.com/skull-01/script.oppo203.iso.external/pull/272)** the configurator's **first CI** — `.github/workflows/configurator-ci.yml`: windows-latest gate (`npm ci` → `tsc -b` + `vite build` → vitest → bundle add-on → `cargo test`) on every configurator-touching PR; a `configurator-v*` tag builds MSI/NSIS + publishes the release as Latest. The first run caught a real gap (tauri `build.rs` needs the bundled add-on zip) before it could bite a release.
- **[#273](https://github.com/skull-01/script.oppo203.iso.external/pull/273)** dashboard **diagnostics export** — pure `diagnostics.ts` + `DiagnosticsCard` + Rust `diagnostics_env`/`write_diagnostics`; sanitized JSON (secrets redacted via the shared redactor) saved to app-data + copy-to-clipboard.
- **[#274](https://github.com/skull-01/script.oppo203.iso.external/pull/274)** installer **single prompt** — the PREINSTALL hook is scoped to the parallel-MSI case Tauri's reinstall page misses, so a normal NSIS upgrade shows one prompt, not two (a full template override needs Tauri's versioned handlebars template — not safely authorable offline).
- **[#276](https://github.com/skull-01/script.oppo203.iso.external/pull/276)** add-on **property tests** (`tests/test_property_http_hdmi.py`, Hypothesis-or-fallback) — caught + fixed a real `OverflowError` on `int(float('inf'))` in `http_info_indicates_playing` (issue **[#275](https://github.com/skull-01/script.oppo203.iso.external/issues/275)**, SHA-commented + OPEN).
- **[#277](https://github.com/skull-01/script.oppo203.iso.external/pull/277)** **i18n scaffold** — `i18n.ts` (`t()` + typed English catalog + `setLocale`); migrated `WinShell` as the first consumer. English-only; remaining screens migrate incrementally against the pattern.
- **[#278](https://github.com/skull-01/script.oppo203.iso.external/pull/278)** bump → tag **`configurator-v0.8.6`**, built + published as Latest by the new CI release job (bundles add-on v2.9.15).
Gates green throughout — configurator: `tsc -b` / vitest / `cargo test` on windows CI; add-on (#276): pytest **1158/3**, **serial coverage 99%**, mypy `--strict` 51/0, ruff clean. **Phase C (operator, real Windows host):** diagnostics export, installer single-prompt, and installing v0.8.6 — see the EOD #14 batch entry in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. **Resume (configurator):** continue incremental i18n migration of the remaining screens against the `t()` pattern, or a fresh theme. **Releases are now `git tag configurator-v*` → CI publishes** (the manual `npm run dist` of [[configurator-release-is-manual]] still works as a fallback). Memory updated: [[configurator-release-is-manual]] now notes the CI path.

**Same-day follow-ups → configurator `v0.8.7`:** added the **Hisense E8N Pro** to the TV DB ([#280](https://github.com/skull-01/script.oppo203.iso.external/pull/280); new `hisense-china-android` lineup, Android/JUUI ≠ VIDAA/Google TV; `custom_command`+`adb`; live to the in-app **"Update database"** button via `main`'s docs copy), **hid the Step 0 "Not yet" button** ([#281](https://github.com/skull-01/script.oppo203.iso.external/pull/281); the OPPO NAS-access path `step0_exit` is dormant, not deleted — restore the button to re-enable), and added **TV-step family screen sizes** for user reassurance ([#282](https://github.com/skull-01/script.oppo203.iso.external/pull/282); optional `sizes` array rendered as a "Sizes: 65″ · 75″ · 85″ · 100″" line + a "listed by family, every size covered" note; control path stays size-independent). The two UI changes (#281/#282) are code, so they ship in a **build** (not the Update-DB button); cut **[configurator-v0.8.7](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.7)** via the CI tag path (MSI 3,694,592 B + NSIS 2,556,655 B + SHA-256; bundles add-on v2.9.15; **holds "Latest"**). Evidence: `configurator/release-evidence/v0.8.7/BUILD_NOTES.md`. Phase-C for the E8N Pro control path + the installed-build UI on real hardware.

---

**As of 2026-06-03 (EOD #13 — #263 Reset-all reachability SHIPPED; cut configurator v0.8.4, holds "Latest").**
**Clean stopping point — no configurator work in flight; `main`@`f437567`; 0 open PRs; gate green (tsc 0 · 304 vitest · vite build · tauri release build).**
Operator picked `resume` → Configurator → **#263** (the queued theme), then **"go"** twice (build, then ship). Fixed the bug that **Reset all configurations** rendered only on the Live dashboard — reachable only via `go("dashboard")` from the final test screen, after a completed setup — so a fresh/broken install (exactly when you'd reset) couldn't find it:
- **[#264](https://github.com/skull-01/script.oppo203.iso.external/pull/264) `285b5e3` (merged `473df58`)** — new `reset_all` utility screen (`configurator/src/screens/ResetAll.tsx`) that **reuses `ResetAllCard` unchanged** (+ a "← Back" to Step 0), surfaced from two persistent entry points: a "Reset all…" button in the app header (`App.tsx`, every screen, hidden only on the reset screen itself) and a "Reset all configurations…" link on the Step 0 gate (`Step0Gate.tsx`). `steps.ts` adds `reset_all` to `ScreenId` + both exhaustive maps (`SCREEN_TO_STEP`→`step0`, `SCREEN_TO_CHAIN`→`media`); new pure `steps.test.ts` pins the wiring (tsc enforces the map presence). **Dashboard card + the reset action (`reset.ts`, Rust `reset_box_*`/`reset_app_data`) untouched.** Gate: tsc 0 · **304 vitest** (+3) · vite build; **browser-verified** (vite): both entries reach the reset screen, the reused danger card reveals its confirm gate, Back returns to Step 0, header entry hidden on the reset screen, no console errors.
- **[#265](https://github.com/skull-01/script.oppo203.iso.external/pull/265) (merged `f437567`)** — bump v0.8.3→**v0.8.4** across `package.json` / `tauri.conf.json` / `Cargo.toml` / `Cargo.lock` (pinned by `version.test.ts`).
- **Release [configurator-v0.8.4](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.4)** via manual `npm run dist` ([[configurator-release-is-manual]]) — MSI 3,682,304 B (`f422aa8e…`) + NSIS 2,542,219 B (`fa6d28ea…`) + SHA-256, unsigned; **bundles add-on v2.9.15** (verified inside the zip); **holds the repo "Latest"**.
**#263 SHA-commented + OPEN** (only-operator-closes); Phase-A/C row in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. **Resume (configurator) — Phase-C** on a real Windows host / Kodi box: confirm the reachability entries on a fresh install, then run the actual reset (deletes add-on + deployed files → first-run; the on-box deletion path is unchanged from v0.8.2 and not hardware-validated). Optional follow-up still open: consolidate the installer to a single old-version prompt (suppress Tauri's built-in reinstall page via a custom NSIS template). Otherwise pick a fresh theme.

---

**As of 2026-06-03 (EOD #12 — audit remediation + TV DB + reset-all + installer check; cut v0.8.1/v0.8.2/v0.8.3).**
**Clean stopping point — no configurator work in flight; `main`@`49972f5`; 0 open PRs; gate green (tsc 0 · 301 vitest · cargo · vite build).**
A long configurator session off the **full audit**, plus three operator feature asks, plus three releases:
- **Audit fixes:** **C1** [#245] (H3 debug-log secret masking of the `settings.xml` blob, M4 single-owner live
  monitor, M8 SSH timeouts + capped HTTP read + deploy rollback, L3 `reveal_path` validation, L6, L9 mutex-poison
  recovery) + **C2** [#253] (M6 step-number banner/label sweep, M7 controlled Player-IP input, L5 deriveRewrite
  backslash, L7 ADB heuristic, L8 `Step0Exit`, L14 password field, L16 routing echo).
- **TV DB +110 TCL/Hisense rows** [#258] (2018–2026; 350→460; 9 overwritten; both copies byte-identical, guard green).
- **Reset-all-configurations** Danger-zone action [#260] — Rust `reset_box_ssh`/`reset_box_userdata`/`reset_app_data`
  delete only the 4 configurator-owned box paths + clear app-data; `reset.ts` + `ResetAllCard.tsx`.
- **Installer old-version check** [#262] — NSIS `NSIS_HOOK_PREINSTALL` (`installer-hooks.nsh`) detects our NSIS
  install + any MSI install and offers to remove all old versions before installing.
- **Three releases** (manual `npm run dist`, each held "Latest" in turn): **configurator-v0.8.1** (audit fixes +
  TV DB; bump PR #259), **v0.8.2** (reset-all; bump PR #261), **v0.8.3** (installer check; PR #262). All bundle
  add-on **v2.9.15**, unsigned, software-verified only. v0.8.3 holds "Latest". Evidence in `release-evidence/v0.8.{1,2,3}`.
**Resume (configurator) — ▶ NEXT THEME (queued):** make the **Reset-all action reachable** (**[#263](https://github.com/skull-01/script.oppo203.iso.external/issues/263)**, `type:bug`). The reset shipped in v0.8.2/v0.8.3 but renders **only** on the Live dashboard (`ResetAllCard` in `screens/dashboard.tsx`), and the dashboard is reachable **only** via `go("dashboard")` from the final test screen (`screens/test.tsx:1232`) — so on a fresh install or a broken/partial setup (exactly when you'd reset) it can't be found, i.e. it looks missing. Fix: add a "Reset all configurations" entry to a persistent / always-reachable location — the app header/shell (visible on every screen) and/or the first screen (Step 0) — keep the dashboard card, then cut **configurator v0.8.4** (configurator release bundling the add-on). **Then Phase-C** on a real Windows host / Kodi box — verify the **reset action** (deletes the
add-on + deployed files; resets to first-run) and the **installer old-version prompt** (detect + remove old
versions); both scripted in the v0.8.2 / v0.8.3 BUILD_NOTES. Optional follow-up: consolidate the installer to a
single old-version prompt (suppress Tauri's built-in reinstall page via a custom NSIS template). Standing rule:
a bare "release" = the configurator release bundling the add-on (see [[configurator-release-is-manual]]).

---

**As of 2026-06-02 (EOD #11 — Xnoppo V3 / Pure-HTTP SHIPPED; configurator `v0.8.0` released, holds "Latest").**
**Clean stopping point — no configurator work in flight; `main`@`be196ac`; 0 open PRs.**
The configurator slices of the Pure-HTTP initiative merged this session — **PR2** the "Pure HTTP" Step-4 pill
(sets both axes → `http_handoff_http`), **PR4** the **Pure-HTTP default flip** (`INITIAL_STATE.monitorMode="http"`)
+ the dashboard's **HTTP process-monitor transport** (`oppo-http` liveness kind, reuses `oppo_playback_info`)
+ the **Refresh Rate** setting, **PR6** the BDMV toggle (`oppo_bdmv_checkfolder`), **PR5** the HDMI-timing
settings (`hdmi_switch_mode`/`play_delay_hdmi`/`av_delay_hdmi`). Then cut **stable configurator `v0.8.0`** via the
manual `npm run dist` ([[configurator-release-is-manual]]) — MSI 3,682,304 B + NSIS 2,538,677 B + SHA-256,
unsigned; **bundles add-on v2.9.15** (confirmed inside the MSI); **holds the repo "Latest" badge**. `state.ts`
`MonitorMode` gains `"http"`; `step2.tsx` no longer overrides an explicit `http` choice; Step-4 copy makes Pure
HTTP the recommended default. Gate: `tsc --noEmit` 0 + **294 vitest** + `vite build`; **browser-verified** the
Step-4 Pure HTTP default + the pill selecting. ENH **#215** (+ the cross-area **#209**) SHA-commented + **OPEN**.
**Resume (configurator), pick one (per §4):** Phase-C the guided install + dashboard with Pure HTTP on real
hardware (operator); or a fresh theme. See [[xnoppo-v3-pure-http-shipped]].

---

**As of 2026-06-02 (EOD #10 — merged the cfg queue + shipped configurator v0.7.0; Pure-HTTP build queued as the NEXT THEME).**
This session **merged the 7-PR draft queue** to `main` (dashboard-memory #200→#201→#202, shared preset #203,
China TV #204; stale #165/#166 closed + branches deleted), then cut **configurator `v0.7.0`** (stable; MSI
3,674,112 B + NSIS 2,527,350 B + SHA-256; **holds the repo "Latest" badge**; bundles add-on **v2.9.14**) and
the standalone add-on **v2.9.14**. Combined `main` green (tsc + 290 vitest + vite build · cargo 40 · pytest
1053/3). 0 open PRs; `main`@`c200349`. Configurator issues **#167/#168/#103/#105** remain **open for operator
close** (implemented + shipped). **▶ NEXT THEME (queued): the Pure-HTTP/436 control initiative — PRs 1–6**,
fully specified in [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) (**Active initiative**) + decision tree
`build/configurator_decision_tree.html`. **Cross-area**; the configurator slices are the "Pure HTTP" Step-4
pill (PR2), default flip + process-monitor TCP/HTTP (PR4), selectable HDMI switching (PR5), the BDMV toggle
(PR6). **Resume → pick the Pure-HTTP theme; Session A = PR1 + PR2.**

---

**As of 2026-06-02 (EOD #9 — "do all cfg": #103/#105 found already-shipped, dashboard-memory stack built + 3 follow-on cfg PRs; 6 draft PRs queued, 0 merged).**
**Clean stopping point — all work committed + pushed across 6 draft PRs + 2 `main` docs commits; `main`@`d1fe1dc`; working tree clean; nothing left on this machine.**
Operator picked `resume` → **"do all cfg"** (the 3 open cfg themes). **Grounding finding:** #103 (TV DB → schema v2) and #105 (canonical players DB) were **already fully implemented on `main`** (TV DB `schema_version:2`, 324 models, region-filter UI; players DB two-copy + `playersdb.ts` + `tests/test_players_db_consistency.py`). Evidence-commented both issues + added a "re-confirmed green on current `main`" note to their checklist rows (pushed `516d465`); **ready for the operator to close**. So the only real build was the **dashboard-memory stack** (#167/#168), rebuilt on the current (Phase 5.2/5.3) dashboard since the stale drafts #165/#166 now conflict:

- **[#200](https://github.com/skull-01/script.oppo203.iso.external/pull/200) `3c4ed10` (base `main`)** — appdata JSON store: Rust `read_app_json`/`write_app_json` guarded by `safe_app_rel` + `dashboard_store.ts`. Foundation. Gate: cargo **40** (+3 `safe_app_rel`), tsc, vitest 261.
- **[#201](https://github.com/skull-01/script.oppo203.iso.external/pull/201) `bc4a8d1` (#167, base = #200 branch)** — settings-snapshot diff card: salvaged #165's `settings_diff.ts`/`dashboard_snapshot.ts`; factored `parseSettingsXml` from `mergeSettingsXml` + `fileReadPlan` from `statusReadPlan` (behaviour-identical, frozen guards held); `isSensitiveKey` masks secrets **before** persist AND diff. Gate: tsc / **273 vitest** / build.
- **[#202](https://github.com/skull-01/script.oppo203.iso.external/pull/202) `bdfd00c` (#168, base = #201 branch)** — session-history card + **exact `session_id` dedup** (the 5.1 unlock): new pure `session_log.ts` `foldObservation` prefers `OppoSessionStatus.sessionId`, heuristic fallback when null; cap 50; same-ref-on-no-change. Gate: tsc / **283 vitest** / build.

Then the operator directed three more cfg items (software + browser verified; no add-on runtime change):

- **[#203](https://github.com/skull-01/script.oppo203.iso.external/pull/203) `ddca058` — shared playback-preset source (cross-area):** new `configurator/src/presets-db/playback-presets.json` is the single source of truth for the six-option matrix; `presetsdb.ts` + `presetsdb.test.ts` pin the TS side, add-on **`tests/test_playback_presets_consistency.py`** pins it to `settings_reader`'s `PLAYBACK_ARCHITECTURE_PRESETS`/`_PRESET_BY_AXES`/`_ROUTING_ALIASES` (the players-DB-guard pattern), and `mapping.test.ts`'s `CANONICAL_SIX` now **derives from the DB** (manual mirror gone). **No runtime change.** Gate: add-on `pytest -n auto` **1053/3** + `ruff` clean; cfg tsc / **266 vitest** / build.
- **[#204](https://github.com/skull-01/script.oppo203.iso.external/pull/204) `f11ffb9`+`159a1ab` — TV DB +26 China models (`CN` region) + `tv_ip` comment fix:** TV DB **324→350** families — 2 new lineups (`tcl-china-android` Android/雷鸟系统→`adb`; `hisense-china-vidaa` VIDAA/聚好看→`custom_command`) + 13 TCL (incl. FFALCON 雷鸟) + 13 Hisense ULED; `tvdb.ts` `TvRegion`+`TV_REGIONS` gain `CN` (Step-5 pill auto-renders); both `tv-models.json` copies byte-identical; all `validated:false`/`low`. **Browser-verified** the CN pill + 13 China TCL families render. Also fixed the stale `mapping.ts` `tv_ip` comment (it IS emitted since #198/#199). Gate: tsc / **263 vitest** (+2 CN) / build.
- **`docs/BUILD_PLAN.md` refreshed** on `main` (`d1fe1dc`): header declares the guided-install initiative software-complete with a Phase→PR map; §4 carries a ✅ DELIVERED banner.
- **Fullwired audit** (operator asked "is the configurator and addon fullwired?"): confirmed **fully software-wired** — all 43 `mapping.ts`-emitted keys are read by the add-on; the 4 architecture/preset keys are read from the runtime `settings.xml` the configurator writes (`settings_reader.read_settings` parses every `<setting>`, not just schema-declared); the 64 unset `settings.xml` ids are advanced-tuning / in-add-on defaults by design; 32 Tauri cmds all UI-invoked.

**Resume here next (configurator), pick one (per §4):**
1. **Merge the queue** — dashboard stack bottom-up (#200→#201→#202, **retarget each child to `main` first**), then #203 + #204 (both merge straight to `main`); **close the stale #165/#166** (superseded by #201/#202) and the 4 implemented cfg issues (#103/#105/#167/#168). ([[stacked-pr-local-merge-status]])
2. **Cut the configurator release** — `main` carries all of Phases 1–5 + this session's work since the last published `v0.5.0`; D-1=C bundles `main` fresh (incl. the 5.1 add-on status). The `/release` skill.
3. **Phase-C hardware validation** — the whole guided-install flow + the dashboard cards + the China TV control paths, on real hardware (operator; no agent code).

---

**As of 2026-06-02 (this session — ALL of Phases 3/4/5 built + MERGED to `main`; 13 PRs).**
**Clean stopping point — all work merged to `main`; 0 open PRs from this session; nothing left on this machine.**
Operator picked `resume` → "build all of Phases 3/4/5, full auth, **merge to main as I go**, **finer PRs**, **file ENH issues**."
Delivered the **Rust + add-on backend layer** the UI phases depend on. **Foundation merged first:**
[#174](https://github.com/skull-01/script.oppo203.iso.external/pull/174) (Phase 1b NAS capture) +
[#175](https://github.com/skull-01/script.oppo203.iso.external/pull/175) (D-3 enablement, DRY'd onto `kodi_jsonrpc_cmd`).
**Then 4 backend PRs:**
- **Phase 3.1 AVR** — [#177](https://github.com/skull-01/script.oppo203.iso.external/pull/177) `2bf0663` (issue #176): `avr_switch_denon`/`_eiscp`/`_yamaha`/`_sony_audio` + pure builders (Denon `SI` :23, eISCP `!1SLI` framed :60128, Yamaha `setInput` :80, Sony Audio `setPlayContent` POST).
- **Phase 3.1 TV** — [#179](https://github.com/skull-01/script.oppo203.iso.external/pull/179) `9aa9e1c` (issue #178): `tv_switch_sony_bravia` (HTTP); `tv_switch_adb`/`tv_switch_external` run on the Kodi box **over SSH** like the add-on; `smartthings_switch_request` (builder; HTTPS deferred — no TLS crate). Complements Roku.
- **Phase 4.1** — [#181](https://github.com/skull-01/script.oppo203.iso.external/pull/181) `0b5a8f1` (issue #180): `oppo_power` (off/on/eject → `#POF`/`#PON`/`#EJT`) delegating to `oppo_query`. (activate/signin/play already in #174.)
- **Phase 5.1 (🟦 add-on)** — [#183](https://github.com/skull-01/script.oppo203.iso.external/pull/183) `332c0ba` (issue #182): richer `oppo203iso-status.json` — `session_id`/`started_at`/`updated_at`/`phase` + mid-session heartbeat. Ships on next configurator build (D-1=C). See §3a.

Gate green on `main`: **cargo 35 / tsc / 190 vitest / vite build**; add-on **pytest 1046/3, mypy --strict 51/0, ruff clean, coverage 99%** (`playback_session.py` 100%). All **software-verified ONLY — hardware-pending** (every switch/power path opens one short-lived socket like `tv_switch_roku`; none tried against a real TV/AVR/OPPO). ENH #176/#178/#180/#182 SHA-commented + left OPEN. Checklist Phase A/C rows added per PR.

**UI layer COMPLETE — built by 3 parallel sub-agents (operator: "run it as parallel sub-agents"), all MERGED to `main`:**
- **3.2** switch-and-verify ([#184](https://github.com/skull-01/script.oppo203.iso.external/pull/184), issue #191) · **3.3** auto-find ([#188](https://github.com/skull-01/script.oppo203.iso.external/pull/188), #192) — `step5.tsx` (new `step5_switch.ts`/`step5_autofind.ts`).
- **4.2** test-ISO copy + Rust `copy_to_share` ([#185](https://github.com/skull-01/script.oppo203.iso.external/pull/185), #193) · **4.3** live SVM3 ([#187](https://github.com/skull-01/script.oppo203.iso.external/pull/187), #194) · **4.4** self-test orchestration ([#190](https://github.com/skull-01/script.oppo203.iso.external/pull/190), #195) — `test.tsx` (+ `svm3_confirm.ts`/`self_test.ts`).
- **5.2** dashboard consume + TV liveness + auto-start ([#186](https://github.com/skull-01/script.oppo203.iso.external/pull/186), #196) · **5.3** full-chain view ([#189](https://github.com/skull-01/script.oppo203.iso.external/pull/189), #197) — `dashboard.tsx` (+ `dashboard_chain.ts`, `oppo_status.ts`).

Combined-`main` gate green: **tsc / 247 vitest / vite build / cargo fmt + 37 cargo tests / zero warnings**. ENH **#191–#197** SHA-commented + left OPEN; Phase A/C rows in the checklist. All **software-verified ONLY — hardware-pending**. **Deferred:** `session_id` exact-dedup in `session_log.ts` (that file isn't on `main` — it lived only on unmerged draft #166); `parseOppoStatus` now exposes `sessionId` so it's a one-liner once that session-log work lands.

**Nothing left to BUILD for Phases 3/4/5.** The only remaining work is **operator Phase-C hardware validation** of the whole guided-install flow (install → SSH-first → HDMI switch → OPPO self-test → monitor) on a real Kodi/OPPO/TV/AVR — `docs/MANUAL_VERIFICATION_CHECKLIST.md` has the per-phase steps. The configurator bundles `main` fresh (D-1=C), so the next build carries everything including the add-on status change (5.1). **Follow-up (same session, operator directives "close the verification queue, keep the checklist" + "fully wire everything"):** (1) **Cleared the manual-verification queue** — closed the 23 implemented/SHA-commented confirmation-queue issues (this session's #176/#178/#180/#182/#191–#197 + already-merged prior #173/#150–#152/#111–#117/#123/#113) so nothing is blocked; **kept** `docs/MANUAL_VERIFICATION_CHECKLIST.md` as the on-device record. Left open: #167/#168 (their PRs #165/#166 are unmerged + now `CONFLICTING` against the evolved dashboard), #103/#105 (DB backlog), #44 (tester-solicitation umbrella). (2) **Fully wired TV-backend config persistence** ([#198](https://github.com/skull-01/script.oppo203.iso.external/pull/198), issue #199): `mapping.ts` now persists every TV backend's runtime config (`sony_psk`; adb keyevent shells; lg/samsung/custom `{tv_ip}` command templates; smartthings token/device/oppo+kodi input ids + ack), so the add-on can drive all of them — the AVR side was already complete. An audit confirmed **all 32 Tauri commands are invoked from the UI (zero dead) with no functional stubs**; SmartThings stays build-and-display in the configurator's own test (no TLS crate) but is fired by the add-on at runtime now that its config is persisted. **Mechanics note:** the 7 UI PRs were built as 3 stacked sets; merged bottom-up by retargeting each stacked child to `main` first ([[stacked-pr-local-merge-status]]).

---

**As of 2026-06-02 (EOD #7 — merged guided-install to `main`; built Phase 1b NAS-path capture (#174);
resolved D-2/D-3 + built D-3 (#175)).** **Clean stopping point — all work committed + pushed; `main`@`7554c15`;
2 open draft PRs (#174, #175); nothing left only on this machine.** Operator picked `resume` → configurator,
then drove the build through a series of decisions:

- **Merged the guided-install initiative to `main`.** Operator chose "merge #170/#171/#172 first." Merged the
  already-conflict-resolved **experimental3 integration branch → `main`** (`b927b33`, clean automerge); #170/#171/#172
  all show **MERGED**; configurator is now **0.6.0** on `main`. Gate green on the merge: `cargo test`, `tsc --noEmit`,
  **180 vitest**, `vite build`.
- **Phase 1b — NAS-path capture (observe-and-verify; D-4, issue [#173](https://github.com/skull-01/script.oppo203.iso.external/issues/173)) → draft [#174](https://github.com/skull-01/script.oppo203.iso.external/pull/174).**
  Branch `claude/cfg-nas-path-capture-7c4e9a02` (off the integration base, rebased onto the merged `main`). Makes the
  `http_handoff_svm3` default *settable* (no longer inert): `kodi_now_playing` (Kodi JSON-RPC `Player.GetActivePlayers`→`GetItem{file}`
  over SSH + `kodi.log` fallback) · `oppo_http_play` (activate UDP→`/signin`→`/playnormalfile?payload=`, raw HTTP/1.0 over
  TCP:436 — **pulled forward from Phase 4 PR-4.1**, no new crate) · pure `deriveRewrite`+`parseOppoPlayingPath` (`nas_path.ts`)
  · `oppo_playback_info` (best-effort `/getmovieplayinfo`) + the **OPPO media-path capture card** on the Player step
  (`step2.tsx`): observe-both-ends (Capture-from-Kodi / Read-from-OPPO) + a manual **SMB/NFS** fallback (WebDAV/FTP out of
  scope — the OPPO can't necessarily mount them). Gate: **cargo 18 / 190 vitest / `tsc` / `vite build`**. **Browser-verified**
  (vite dev server): card renders, `deriveRewrite` preview computes (`smb://10.0.1.10/`→`MyNAS/`), "Use this mapping" persists,
  no console errors. Issue #173 filed + SHA-commented; checklist Phase A/C row added. **No add-on change** (`resources/`
  untouched → addon suite stays 1045/3).
- **Resolved D-2 + D-3** (`docs/BUILD_PLAN.md`, `7554c15` on `main`): **D-2** → user-supplies the master ISO; PR-4.2 ships
  **placeholder wiring** (real test uses the operator's disc). **D-3** → enable via Kodi JSON-RPC `Addons.SetAddonEnabled`,
  **manual-restart fallback** if it fails.
- **D-3 built → draft [#175](https://github.com/skull-01/script.oppo203.iso.external/pull/175).** Branch
  `claude/cfg-phase4-prep-iso-enable-3f9c1a07` (off `main`). `kodi_set_addon_enabled` (JSON-RPC over SSH; pure
  `kodi_enable_body`/`kodi_enable_ok`) + `apply.ts` Tier-A wiring that appends a "couldn't auto-enable — restart Kodi /
  enable in Add-ons" message on failure. Gate: **cargo 11 (+2) / `tsc` / 180 vitest**. (Inlines the curl-over-SSH call —
  DRY against #174's `kodi_jsonrpc_cmd` once that merges.)
- **Everything software-verified ONLY — hardware-pending:** the SSH/UDP/TCP I/O, the OPPO activate+signin+play handshake,
  whether `/getmovieplayinfo` carries the path, and real end-to-end capture+play+enable. **Cheap unlock:** run the existing
  "Probe OPPO player status" diagnostic while a file plays and paste the raw `/getmovieplayinfo` body — decides whether OPPO
  capture is automatic vs. manual.

**Resume here next (configurator), pick one (per §4):**
1. **Build PR-4.2 (D-2 test-ISO copy, placeholder)** on the #175 branch — a Rust `copy_to_share` (chunked + progress events) +
   a self-test UI field (`test.tsx`) for the user-supplied ISO source + a progress bar. ← the teed-up next step.
2. **Wire the verify-by-playing UI loop** (the deferred #174 slice) — a "test by playing" button → `oppo_http_play` + a live
   SVM3 `@UPL PLAY` watch (the primitive is in; the wrapper is hardware-gated).
3. **Review + promote #174 and #175** to ready and merge (both software-verified; #174 off the integration base now on `main`).
4. **Phase 3 remaining switch backends** (adb / Sony / SmartThings / LG / Samsung / custom TV + the 5 AVR) — the most
   self-contained, fully software-verifiable theme.

---

**As of 2026-06-01 (EOD #6 — guided-install initiative: install + SSH-first flow + Roku switch; 3
experimental builds).** **Clean stopping point — nothing in flight; `main` code unchanged (docs/norms
only); the work lives on 4 branches + 3 draft PRs + 3 pre-releases; nothing merged to `main`.** A very large
session that turned the configurator from a config-writer into a guided installer + monitor, built across
independent branches off `main` (all **software-verified only, hardware-pending**):
- **Phase 1 install** (`claude/cfg-phase1-install-addon-5c1d8a30`) → **PR
  [#170](https://github.com/skull-01/script.oppo203.iso.external/pull/170)**: bundles the add-on ZIP as a
  Tauri resource + `install_addon` Rust (Tier A SSH `python3 -m zipfile` / B `zip`-crate extract / C manual)
  + `installAddonToKodi`; default preset → `http_handoff_svm3`; configurator → **0.6.0**. Released
  **`configurator-v0.6.0-experimental2`** (MSI/NSIS).
- **Phase 2 SSH-first flow** (`claude/cfg-phase2-ssh-first-flow-9b2e7c41`) → **PR
  [#171](https://github.com/skull-01/script.oppo203.iso.external/pull/171)**: re-sequenced the wizard to
  gate→**Kodi/SSH(1)→HDMI switcher(2)→Player(3)**→…→AVR(7)→✓ (new `step_switch` step; ids kept stable, a
  **documented id↔number divergence** in `steps.ts`; **browser-verified** via vite click-through); honesty
  **de-stub** of the step-5 switch + test-disc simulations; **persist TV IP** → `tv_ip` + dashboard TV liveness.
- **Phase 3 slice Roku switch** (`claude/cfg-phase3-hdmi-switch-4f8a2c19`) → **PR
  [#172](https://github.com/skull-01/script.oppo203.iso.external/pull/172)**: `tv_switch_roku` (validated
  ECP `POST /keypress/<key>` :8060), cargo-tested.
- **Integration** (`claude/cfg-experimental3-integration` `5dcb087`): merged all 3 (resolved a `lib.rs`
  handler/test conflict — kept both command sets); cargo **9/9** · tsc · **180 vitest** · build. Released
  **`configurator-v0.6.0-experimental3`** (cumulative MSI/NSIS).
- Merged to `main`: the **six-preset matrix guard** (PR
  [#169](https://github.com/skull-01/script.oppo203.iso.external/pull/169) `de6622a`) + its norm;
  `docs/BUILD_PLAN.md` rewritten for the whole initiative (decisions **D-A** http_handoff_svm3 / **D-B**
  full-ISO test / **D-C** one-package-not-six-builds / **D-1=C** bundle `main` fresh).

**Bottom line: every hardware path (SSH install+unzip, OPPO HTTP play, Roku switch) is software-verified
ONLY — none on real Kodi/OPPO/TV; the `http_handoff` default is inert until the OPPO NAS-path capture UI.**
**Resume (configurator):** (1) run a pre-release (`experimental3`) on real hardware and fix from failures;
or (2) review/promote the 3 draft PRs (#170–172) to ready + merge. **Paused pending hardware:** Phase 3's
other backends (adb / Sony / AVR) + the switch-and-verify UI; Phase 4 (OPPO power-cycle + ISO copy + play,
which needs the OPPO NAS-path capture). The EOD #5 dashboard-memory stack (#165/#166) is still open below.

---

**As of 2026-06-01 (EOD #5 — dashboard follow-on: settings-snapshot diff + session log).** **Clean
stopping point — no configurator work in flight; `main` code unchanged at `b098fd4`; 2 NEW stacked draft
PRs + 2 NEW ENH issues; nothing merged.** This session built **Configurator theme 3 — Dashboard
follow-on** ("give the dashboard a persisted memory") as a 2-PR stack (software-verified only), then filed
the matching ENH issues:

- **[#165](https://github.com/skull-01/script.oppo203.iso.external/pull/165) (1/2 — settings-snapshot diff)**
  `9b15e93` (base `main`; branch `claude/cfg-dashboard-snapshot-91ea2784`). A **Configuration changes**
  card on the Live dashboard: a **Snapshot now** button reads the box's `settings.xml` over a new shared
  `fileReadPlan(state, rel)` (factored from `statusReadPlan` — identical behaviour), parses it with a new
  exported `parseSettingsXml` (factored from `mergeSettingsXml` — identical behaviour), **sanitizes
  secret-bearing ids** (`sony_psk`/`smartthings_token`/`sony_avr_psk` → a fixed `[secret]` via the shared
  `debug/log.ts` `isSensitiveKey`), persists the sanitized snapshot, and diffs it against the prior one
  (added/removed/changed; first capture is a baseline). New Rust `read_app_json`/`write_app_json` — a
  `safe_app_rel`-guarded (no `..`/absolute) appdata JSON store modelled on `save_wizard_state`. New
  `settings_diff.ts`/`dashboard_store.ts`/`dashboard_snapshot.ts`. Tracks **#167**.
- **[#166](https://github.com/skull-01/script.oppo203.iso.external/pull/166) (2/2 — historical session log)**
  `1408eab` (base = #165's branch; branch `claude/cfg-dashboard-session-log-16f907e6`). A **Session
  history** card: each 6s poll folds the add-on's overwritten `oppo203iso-status.json` into a persisted
  history via a new pure `session_log.ts` `foldObservation` (in-place advance start→stop; new entry on a
  signature change or a same-media replay after the prior run ended; cap 50; **same-array-ref on no change**
  so idle polls don't churn the appdata write), reusing #165's store. Tracks **#168**. **Heuristic dedup
  caveat:** the add-on `_status` schema has no session id/start timestamp, so two identical back-to-back
  sessions can't be told apart — exactness would need an **addon-area** schema field (`session_id`/
  `started_at`), out of scope this session.

Gate on the PR-166 tip (which includes #165): `tsc --noEmit` 0 / **194 vitest** (+19) / `cargo test` **8**
(+3 `safe_app_rel`) / `vite build`. **No add-on change** (`resources/` untouched → addon suite unaffected,
stays **1045/3**); **no new crate dependency**. Frozen guards held (`mergeSettingsXml` `/refusing to
overwrite/`, `statusReadPlan` routing, `redact`), pinned by their existing tests. Both ENH **#167/#168**
(`area:configurator`) SHA-commented + left **open** (only-operator-closes); Phase A/C rows in the checklist.
14 files, all `configurator/` + the checklist (verified: addon untouched).

**Resume here next (configurator), pick one (per §4):**
1. **Review + merge the dashboard-memory stack** [#165](https://github.com/skull-01/script.oppo203.iso.external/pull/165) → [#166](https://github.com/skull-01/script.oppo203.iso.external/pull/166) (bottom-up — ⚠️ `gh pr edit 166 --base main` **first**; this repo does NOT auto-retarget, and merging #165 with `--delete-branch` would close #166, [[stacked-pr-local-merge-status]]), then Phase C: open **Live dashboard** → snapshot/diff settings, confirm session history persists across reopen, and **confirm no secret lands in `…\dashboard\settings-snapshot.json`** (only `[secret]`).
2. **Phase C the prior dashboard** (D3 dual-subscriber on a real OPPO, #153 wire panel) + fact-check the 2026 DB rows (#140 AVR / #141 TV `validated:false`).
3. _(optional)_ **Dashboard follow-on round 2** — keep N settings snapshots (history/export), or a settings-snapshot↔wizard-intent diff.

---

**As of 2026-06-01 (EOD #4 — dashboard + wire-transcripts MERGED; "Merge all").** **Clean stopping
point — no configurator work in flight; `main`@`9b0cb6d`; 0 open PRs.** Operator picked **theme 1**
(merge the dashboard stack), then **"Merge all".** Both landed:

- **Live Session Dashboard stack MERGED** bottom-up: D1
  [#158](https://github.com/skull-01/script.oppo203.iso.external/pull/158) `5755184` (device liveness) →
  D2 [#164](https://github.com/skull-01/script.oppo203.iso.external/pull/164) `e4118c0` (current-session
  panel) → D3 [#160](https://github.com/skull-01/script.oppo203.iso.external/pull/160) `e8d35bf` (gated
  live `#SVM 3` stream). ⚠️ **Mechanics casualty:** merging D1 with `--delete-branch` **auto-CLOSED**
  stacked child [#159](https://github.com/skull-01/script.oppo203.iso.external/pull/159) (D2) — this repo
  does **not** auto-retarget, and a closed-base PR can't be reopened. Recovered as **new PR #164**
  (byte-identical D2 code, base `main`). The audit stack (§3a) then merged with **zero** closures by
  retargeting its children to `main` *first*.
- **Wire-level transcripts MERGED** —
  [#153](https://github.com/skull-01/script.oppo203.iso.external/pull/153) `832b76e` (`oppo_query` emits
  `debug-wire` events → the panel shows the raw OPPO bytes, Ctrl+Shift+D). It **conflicted** against the
  now-merged dashboard work; resolved on-branch (merged `main` in): a checklist **union** conflict + a
  **duplicate `#[cfg(test)] mod tests`** in `lib.rs` (both D3 and #153 had added one — `cargo check`
  passed but `cargo test` caught `E0428`; folded into a single 5-test module).

Configurator gate green on merged `main`: `tsc --noEmit` 0 / **175 vitest** / `cargo check` 0 /
`cargo test` **5** / `vite build`. Addon `resources/` untouched by every merge.

**Two merge-mechanics lessons (also pushed to memory [[stacked-pr-local-merge-status]] +
[[rust-duplicate-mod-tests-on-merge]]):**
1. **Stacked `--delete-branch` CLOSES the next child here — it does NOT auto-retarget.** Correct
   procedure: `gh pr edit <each-child> --base main` *before* merging any parent (works while the child
   still has commits not on `main`), then `gh pr merge` bottom-up (prune branches at the end). Proven on
   the audit stack. If a child was already closed, it can't reopen — open a fresh PR from its surviving
   head branch (what #164 did for #159).
2. **A duplicate `#[cfg(test)] mod tests` from a Rust auto-merge is invisible to `cargo check`** (it
   skips `cfg(test)` code) — only `cargo test` (or `cargo check --tests`) surfaces the `E0428`. Always
   run `cargo test` after merging two branches that touch the same `lib.rs`.

**Resume here next (configurator), pick one (per §4):**
1. **Phase C** — dashboard (esp. **D3 dual-subscriber** on a real OPPO, hardware-unverifiable
   in-session), the **#153 wire panel** (Ctrl+Shift+D → raw bytes, confirm no secrets), and the SVM3 /
   http_handoff readouts.
2. **Fact-check the 2026 DB rows** (#140 AVR / #141 TV, all `validated:false`).
3. _(optional)_ **Dashboard follow-on** — historical session log / settings-snapshot diff.

---

**As of 2026-06-01 (EOD #3 — Live Session Dashboard built).** **Clean stopping point — no
configurator work in flight; `main`@`72c84d8` (code unchanged); 3 NEW draft PRs + the prior #153
draft.** This session built **Theme 2 — Live Session Dashboard** as 3 stacked draft PRs
(software-verified only):

- **[#158](https://github.com/skull-01/script.oppo203.iso.external/pull/158) D1 — device liveness:**
  new post-setup `dashboard` screen (a **Live dashboard** button on `TestSuccess`) polling liveness
  every 6s by reusing `tcp_probe`/`oppo_query` — Kodi (SSH 22 / SMB 445), OPPO (`#QPW` power), AVR
  (control port, AVR chain). **TV omitted** — the wizard persists no TV IP. Pure
  `dashboard_targets.livenessTargets` + 5 tests. **No Rust/dep/add-on change.**
- **[#159](https://github.com/skull-01/script.oppo203.iso.external/pull/159) D2 — current-session
  panel:** reads `oppo203iso-status.json` via the existing `read_ssh_file`/`read_userdata_file`
  (tier-aware, like `applyToKodi`); pure `parseOppoStatus` mirrors the add-on `_status` schema;
  honest "start/end summary, not a live feed." +8 tests. **No Rust/dep/add-on change.**
- **[#160](https://github.com/skull-01/script.oppo203.iso.external/pull/160) D3 — gated live verbose
  stream:** new Rust managed `LiveMonitor` + `start/stop_oppo_live_monitor` — a `std::thread` holding
  `#SVM 3`, streaming `@UPL`/`@UTC` as `oppo-live` events, restoring the prior verbose mode on stop
  (**no tokio / no new crate**). **Dual-subscriber gate** `canStartLiveStream` refuses while the
  add-on owns a session + auto-stops mid-stream. Its `oppo-live` channel is **independent of draft
  #153**. +2 vitest + 2 cargo tests.

Gate green: `tsc --noEmit` 0 / **173 vitest** / `cargo check` 0 / `cargo test` 2 / `vite build`.
**D3's dual-subscriber non-conflict is hardware-unverifiable in-session** (the OPPO treats verbose
mode as device-global).

**Resume here next (configurator), pick one (per §4):**
1. **Review + merge the dashboard stack** [#158](https://github.com/skull-01/script.oppo203.iso.external/pull/158) → [#159](https://github.com/skull-01/script.oppo203.iso.external/pull/159) → [#160](https://github.com/skull-01/script.oppo203.iso.external/pull/160) (bottom-up — ⚠️ **corrected EOD #4:** this repo does **not** auto-retarget; `--delete-branch` CLOSES the next child, so `gh pr edit <child> --base main` *first* — see §3b EOD #4 + [[stacked-pr-local-merge-status]]), then Phase C — especially **D3 dual-subscriber** on a real OPPO.
2. **Review + merge PR [#153](https://github.com/skull-01/script.oppo203.iso.external/pull/153)** (wire transcripts, still open) → Phase C.
3. **Fact-check the 2026 DB rows** (#140 AVR / #141 TV `validated:false`).
4. _(optional)_ **Dashboard follow-on** — historical session log / settings-snapshot diff (extends Theme 2).

---

**As of 2026-06-01 (EOD #2 — SVM3 wizard merged + http_handoff + wire-transcripts draft, configurator side).**
**Clean stopping point — no configurator work in flight; `main`@`72c84d8`; one open draft PR (#153).**
This session **merged** the SVM3 wizard stack and the http_handoff routing, and left wire-transcripts as a draft:

- **SVM3 wizard stack MERGED** — #146 `4680278` (Step 3 "Playback mode" + renumber), #147 `f06e1de`
  (SVM3-vs-Legacy choice + emit triple), #148 `caaba1b` (SVM3 capability probe), #149 `f90da27`
  (final-test readout). (#147–#149 show *Closed* not *Merged* — stacked-local-merge artifact; code is on `main`.)
- **`http_handoff` six-option MERGED** — #156 `4b4d950` (HTTP Handoff routing pill on the Kodi-box step
  + emits the `http_handoff_*` preset triple) + #157 `37e50e9` (emits `oppo_http_payload_mode=json_payload`).
  **Caveat:** the OPPO-visible path translation (`oppo_http_path_from`/`_to`) is NOT auto-emitted
  (player/mount-specific — operator config); the NFS/SMB mount endpoints + `/checkfolderhasBDMV` are deferred.
- **Wire-level debug transcripts — OPEN DRAFT [#153](https://github.com/skull-01/script.oppo203.iso.external/pull/153)**
  (`oppo_query` emits `debug-wire` events → the panel shows raw OPPO bytes). Gate green (157 vitest +
  `cargo check`/`cargo test`). **Awaiting operator review → mark ready → merge** + Phase C.

Gate on `main`@`72c84d8`: configurator `tsc -b` + **158 vitest** + `vite build` (addon untouched by the config PRs).

**Resume here next (configurator), pick one (per §4):**
1. **Review + merge PR #153** (wire transcripts) — review → mark ready → merge; then Phase C (Ctrl+Shift+D → see the OPPO bytes).
2. **Theme 2 — Live Session Dashboard** (planned, not started) — post-config dashboard: device liveness (poll the existing probes), current activity (read `oppo203iso-status.json`), and a live SVM2/SVM3 stream (a NEW persistent Rust monitor; **dual-subscriber gated** — see the plan in this session's transcript).
3. **Fact-check the 2026 DB rows** (#140 AVR / #141 TV `validated:false`).

**Reference — the SVM3 wizard stack as originally built (now merged), in order #146 → #147 → #148 → #149:**

- **[#146](https://github.com/skull-01/script.oppo203.iso.external/pull/146) (`df4012c`)** — inserts a
  new **Step 3 "Playback mode"** after Player and **renumbers TV 3→4, HDMI 4→5, AV Receiver 5→6**.
  Mechanical, behavior-preserving rename: `screens/step3|4|5.tsx`→`step4|5|6.tsx`, `Step3|4|5*`→`Step4|5|6*`,
  `step3_*/step4_*/step5_*` ScreenIds, `step4NextScreen`→`step5NextScreen`, `steps.ts` maps + `App.tsx`
  renderers; new placeholder `step3.tsx`; Player routes to `step3_mode`. All step-number display copy +
  comments updated to the new numbering (AGENTS.md "names match the UI"). **No TV/HDMI/AVR/Player logic changed.**
- **[#147](https://github.com/skull-01/script.oppo203.iso.external/pull/147) (`5d24d5f`)** — the Step 3
  screen offers **SVM3** vs **Legacy** (`state.monitorMode`, new `MonitorMode` type, default legacy);
  `mapping.ts` emits the consistent **triple** `playback_architecture` + `playback_monitor_mode` +
  derived `playback_architecture_preset` (which addon #143 reads, treating the preset as source of truth).
  `mapping.test.ts` +5 (four-combo consistency).
- **[#148](https://github.com/skull-01/script.oppo203.iso.external/pull/148) (`27c01d2`)** — the Step 2
  player test runs an **SVM3 capability probe** (`#QVM`→`#SVM 3`→restore) reusing `oppo_query` (**no Rust
  change**); new parsers `parseOppoVerboseMode`/`parseSvm3Accepted` (`probes.ts`, +4); stores
  `state.svm3Supported` and recommends the matching Step-3 default (svm3 if accepted, else legacy);
  never gates the power test.
- **[#149](https://github.com/skull-01/script.oppo203.iso.external/pull/149) (`2dfa86c`)** — the final
  Playback Test screen reports the four-option pieces **separately** (Kodi route / playback confirmation /
  TV-AVR) + an honest SVM3 note (confirmed only once the player reports it). Presentational only.

**Software-verified only:** `tsc -b` + `vite build` + **up to 155 vitest** green on each branch (146
base +5 mapping +4 probes). **No add-on code change** — the configurator emits the keys addon Session A
(#143/#145) reads. SVM3 stays labelled *recommended for validation / new installs*, not hardware-validated.
Phase A/C rows for all four are in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. _(The B1 rename obsoleted a
spawned "fix Step N copy" task chip — that copy was already fixed in #146; the chip is safe to dismiss.)_

**Prior — DB-growth + developer-debug-view session (merged to `main`, `9419bea`):** 4 configurator PRs
(PR-only, merged locally `--no-ff`, checklist rows union-merged, one `step5.tsx` import conflict resolved
to keep `isAvrChain` + route `invoke` through `../ipc`):

- **Dedicated Step-5 receiver restore-input field** ([PR #139](https://github.com/skull-01/script.oppo203.iso.external/pull/139), `90bd36b`) — the PR #138
  follow-up: new `state.avrKodiInput`, captured in a Step-5 "Kodi input on the receiver" field (AVR
  chain, native non-Sony only); `mapping.ts` sources `avr_restore_input` from it instead of reusing
  the TV's `kodiInput`. Blank ⇒ no restore (add-on non-fatal skip, `avr_sequence.py`).
  `avr_restore_input` is `type="string"` ⇒ **no add-on change**. Test summary shows receiver inputs.
- **AVR DB grown — 2026 candidates** ([PR #140](https://github.com/skull-01/script.oppo203.iso.external/pull/140), `5d3fe62`) — +15 `validated:false` 2026
  model rows to both `avr-models.json` copies (Denon X2900H/X3900H, Marantz AV 30, Yamaha RX300A/
  RX500A, Onkyo TX-RZ31/51/61/71, Integra DRX-R1/DRX-7, Arcam AVA15/25/35+AVP45); `db_version` →
  `2026.05.31-avr-2018-2026-region-schema`, `scope.years` → [2018,2026]; `2026` Step-5 year filter.
- **TV DB grown — 2026 lineups + NEW two-copy guard** ([PR #141](https://github.com/skull-01/script.oppo203.iso.external/pull/141), `15cc176`) — +28
  `validated:false` 2026 rows to both `tv-models.json` copies (Samsung 7/LG 6/Sony 2/TCL 7/Hisense 6);
  `scope.years` → [2018,2026]; `2026` Step-3 year filter. New `configurator/src/tv_db_consistency.test.ts`
  pins the two copies byte-identical + invariants (the AVR `#134` guard the TV DB lacked). 2025 was
  already complete (44 rows). Caveats in notes: Hisense platform-by-region (low/med conf), Samsung
  QN90 has no 2026 successor, Sony carried-over 2025 sets stay under 2025.
- **Developer debug view** ([PR #142](https://github.com/skull-01/script.oppo203.iso.external/pull/142), `bf06a69` + `03572ef`) — new `src/debug/log.ts`
  (redacting 500-entry ring buffer + current-step tag), `src/ipc.ts` (an `invoke` wrapper recording
  every call as a pure pass-through; all wizard call sites migrated, so **only `ipc.ts`** imports the
  Tauri `invoke`), and a global docked `src/shell/DebugPanel.tsx` in `App.tsx` showing each command
  (redacted args/result/error/timing) for the current step. **Off by default; Ctrl+Shift+D.** Secrets
  redacted (psk/token/password/secret/credential; blob truncation). PR-3 wire-level Rust transcripts
  **deferred**.

**Post-merge `main`@`9419bea` green (software-only):** configurator `tsc --noEmit` + `vite build`
+ **146 vitest** (123 base +2 restore-input +8 tv-consistency +13 debug-view). **Addon untouched**
this session (configurator + docs only) → stays **976 pass / 3 skip**. **No add-on code change.** All
DB rows `validated:false` (**operator fact-check**); new behaviors are Phase-A/C rows in
`docs/MANUAL_VERIFICATION_CHECKLIST.md` (the 4 rows union-merged on `main`). See
[[configurator-avr-db-no-consistency-guard]], [[configurator-control-tests-are-mocked]].

**Resume here next (configurator), pick one (per §4):**
1. **Review + merge the SVM3 wizard stack (#146 → #147 → #148 → #149)** — review each draft in order
   and merge; then Phase-C the new Playback-mode step + the SVM3 probe in the built app, pairing the
   deploy with addon Session A #143/#145 so the emitted preset/monitor_mode is actually read. ← resume here.
2. **Fact-check + Phase-C the merged 2026 DB rows** — verify the AVR (#140) + TV (#141)
   `validated:false` rows against real product data; especially Hisense platform-by-region,
   Integra model-year, and the Yamaha entry-tier network-control caveat.
3. **Wire-level debug transcripts (PR #142 PR-3)** — emit `debug-log` events from the Rust commands for
   raw sent/received bytes. _(The `tv_port_probe`→`tcp_port_probe` rename flagged in #135 stays
   **declined** — don't re-raise. `state.topology` into `shell/AppHeader.tsx` from #138 is still open.)_
4. **Install + smoke-test the published `v0.5.0` binary** on a clean Windows machine (operator action).

**Prior — 2026-05-31 (EOD) — AVR follow-ups + two-playback-chains session (5 configurator PRs, all merged).** Two themes shipped, all merged:

**AVR follow-ups** (the §3b "scoped, not built" items, now done):
- **AVR DB consistency guard** ([PR #134](https://github.com/skull-01/script.oppo203.iso.external/pull/134), `fbe98d2`) — new `configurator/src/avr_db_consistency.test.ts`
  pins `configurator/src/avr-db/avr-models.json` ↔ `docs/configurator/avr-db/avr-models.json`
  byte-identical + schema invariants (mirrors `version.test.ts`'s `readFileSync(new URL(...))`
  pattern under `// @vitest-environment node`). Closes the no-guard gap — see updated
  [[configurator-avr-db-no-consistency-guard]] (guard now EXISTS).
- **Step-5 receiver reachability probe** ([PR #135](https://github.com/skull-01/script.oppo203.iso.external/pull/135), `721c3ed`) — a **Test reachability** button on
  the AVR control card TCP-probes the receiver control port by reusing the **generic** `tv_port_probe`
  Tauri command (no Rust change): Denon/Marantz 23, Yamaha 80, Onkyo/Pioneer 60128; Sony
  (authenticated HTTP/PSK) + custom_command show no probe. The operator's real-probe flavor (not the
  mocked TV "mute test"). PR body notes `tv_port_probe` is generic despite the `tv_` name (future
  cleanup: rename `tcp_port_probe`). See [[configurator-control-tests-are-mocked]].

**Two playback chains** (operator-directed new theme — make the config steps differ by chain):
- **Step-0 chain picker + `state.topology`** ([PR #136](https://github.com/skull-01/script.oppo203.iso.external/pull/136), `1e8f678`) — new Step-0 "How is your home
  theater wired?" sets `topology: "kodi_tv_player" | "kodi_avr_tv_player"` (`new Step0Chain.tsx`; the
  gate routes into it; `steps.ts` adds `step0_chain`). **Soft default:** a null/legacy topology
  behaves as the TV chain everywhere.
- **Topology-aware flow + chain viz** ([PR #137](https://github.com/skull-01/script.oppo203.iso.external/pull/137), `51a2a0a`) — header chain inserts a **Receiver**
  node for the AVR chain (ISO→Kodi→Receiver→Player→TV); Step-4 copy frames inputs as **receiver**
  inputs. Pure helpers `isAvrChain`/`chainNodeIds`/`step4NextScreen` in `steps.ts`, unit-tested in
  `topology.test.ts`. `<Chain topology?>` is optional so the static summary/`AppHeader` call sites
  are unchanged.
- **Mapping writes the AVR-switcher settings** ([PR #138](https://github.com/skull-01/script.oppo203.iso.external/pull/138), `2ae4b16`) — for the AVR chain
  `mapping.ts` now emits `avr_power_on_enabled` + `avr_restore_enabled`/`avr_restore_input` (reusing
  the Step-4 Kodi input as the receiver restore input; non-numeric CEC/cycle ⇒ no restore input) and
  gates `tv_switching_enabled` **off** (the receiver is the switcher). TV chain unchanged
  (regression-pinned). **No add-on change** — all settings already exist in `settings.xml` and are
  read by `resources/lib/avr/avr_control.py` (`avr_settings_summary`/`validate_avr_settings`).

**Software-verified only** — configurator `tsc -b` + `vite build` + **123 vitest** green each PR
(+ a smoke of addon 976/3). **Not** browser-preview tested (Tauri `invoke` paths don't resolve in a
plain vite preview) and **no hardware** — the real receiver/TV switching + reachability are Phase-C
rows in `docs/MANUAL_VERIFICATION_CHECKLIST.md`. Each PR built off fresh `main` and merged before the
next (so checklist rows never collided). **Open follow-up flagged in PR #138:** the receiver *restore*
input currently reuses `kodiInput`; a dedicated Step-5 "Kodi input on the receiver" field could be
added if a distinct value is wanted. Minor: `shell/AppHeader.tsx` (an unused alternate header) renders
`<Chain>` without `topology` (safe — defaults to TV chain); pass `state.topology` there if it's ever
used.

_That session's resume list is superseded — see the current "Resume here next" near the top of §3b.
Its items shipped this session: the restore-input field as [#139](https://github.com/skull-01/script.oppo203.iso.external/pull/139), and `avr-models.json` growth as [#140](https://github.com/skull-01/script.oppo203.iso.external/pull/140) (plus TV DB [#141](https://github.com/skull-01/script.oppo203.iso.external/pull/141))._

**Prior context (durable) — naming-consistency + Sony/badge (2026-05-31 EOD, HEAD `8c35f28`):**
Sony brand-badge dark-chip fix ([#120](https://github.com/skull-01/script.oppo203.iso.external/pull/120)); **Sony AVR auto-enable** ([#122](https://github.com/skull-01/script.oppo203.iso.external/pull/122) — Step-5 captures Sony
PSK+ack+URI, enables `sony_audio_api` only when complete); v0.5.0 Step-5 checklist entry ([#121](https://github.com/skull-01/script.oppo203.iso.external/pull/121));
naming sweep (`oppoInput`→`playerInput` [#124](https://github.com/skull-01/script.oppo203.iso.external/pull/124); `players.json`→`players-models.json` [#125](https://github.com/skull-01/script.oppo203.iso.external/pull/125);
`CONFIGURATOR_HANDOFF` map [#127](https://github.com/skull-01/script.oppo203.iso.external/pull/127); new `docs/NAMING_CONVENTIONS.md` [#128](https://github.com/skull-01/script.oppo203.iso.external/pull/128)).

**Prior context (durable) — configurator `v0.5.0`:**

**As of 2026-05-30 (later still — configurator `v0.5.0` shipped + published as the repo's
GitHub "Latest").** **Clean stopping point — no configurator work in flight, no open
configurator PRs.** This session delivered the **AVR (AV receiver) feature in two releases**:
- **`v0.4.0` — AVR database + optional Step 5** ([PR #109](https://github.com/skull-01/script.oppo203.iso.external/pull/109), merge `6251cdf`). Built from the operator's
  fact-checked bundle: `configurator/src/avr-db/avr-models.json` (+ canonical `docs/` copy) with
  **224 AV-receiver/processor model families** 2018–2025 across 10 brands (Denon, Marantz, Yamaha,
  Onkyo, Pioneer, Integra, Sony, Anthem, Arcam, NAD), schema v2 — the **TV-DB twin** (lineups +
  models + region_schema, all `validated:false`). New `avrdb.ts` loader (region filtering, backend
  resolution, remote "Update list" refresh) + 18 vitest; new optional **Step 5 (AV Receiver)**
  picker (ask → brand → region/year-filtered model list). The bundle→JSON transform is
  `build/gen_avr_db.py` (git-ignored).
- **`v0.5.0` — wired Step 5 into the add-on `settings.xml`** ([PR #110](https://github.com/skull-01/script.oppo203.iso.external/pull/110), merge `bc3ad0e`), giving Step 5
  true **TV/Player parity** (it was display-only in v0.4.0). A "Receiver control" card captures
  receiver IP + player input; `mapping.avrAddonBackend()` maps the DB backend vocab onto the
  add-on's `avr_backend` enum (verified vs `resources/lib/avr/avr_presets.py`): **Pioneer**
  (DB folds it into `onkyo_eiscp`) → the add-on's distinct `pioneer_eiscp`; **Sony** `sony_audio`
  → `sony_audio_api`. Conservative enable: `avr_control_enabled=true` only for a native non-gated
  driver with host + input present; **Sony** configured-but-off (add-on gates it on ack + PSK);
  **Anthem/Arcam/NAD** (`custom_command`) write no `avr_backend`. Skipping Step 5 emits nothing
  AVR-related, so it never disturbs an existing add-on AVR config.

Published **`configurator-v0.5.0`**: MSI 3,174,400 B + NSIS 2,071,403 B + SHA-256; evidence at
`configurator/release-evidence/v0.5.0/BUILD_NOTES.md` (v0.4.0 evidence under `…/v0.4.0/`).
**Software-verified only** — `tsc -b` + **101 vitest** + `npm run build`, plus a browser-preview
pass of Step 5 (Pioneer→`pioneer_eiscp` enable callout; Sony→configured-but-off); published assets
re-downloaded **byte-identical**. **Not** installed on a clean machine, **no hardware validation**.
All AVR rows are `validated:false` candidate mappings. **No add-on code change** (the AVR DB isn't
loaded by the add-on at runtime; the add-on already ships the AVR settings + guarded drivers).
**Gotcha this session:** publishing the v0.5.0 release was auto-mode-gated (Create-Public-Surface,
because it came from a "continue" follow-up not the original "publish" ask) — approved, then
published. Also a linter touched `step5.tsx` mid-edit and silently dropped the control-card UI on
the first attempt; caught via browser preview, amended, rebuilt, re-verified (see
[[avr-database-configurator]], [[configurator-release-process]]).

- **Prior — configurator `v0.2.0`** ([release `configurator-v0.2.0`](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.2.0),
  full release marked **Latest**, unsigned; SmartScreen "unknown publisher" expected): MSI
  (3,162,112 B, `202d79e7…dc0765`) + NSIS setup (2,059,233 B, `2c0bd3ab…68d0`) + SHA-256
  sidecars; tag `configurator-v0.2.0` at `1b31941`. Evidence:
  `configurator/release-evidence/v0.2.0/BUILD_NOTES.md`. **The repo-wide "Latest" badge moved
  off the add-on `v2.9.13`** — left on the configurator per the operator's `done-for-the-day`
  choice; flip back with `gh release edit v2.9.13 --latest` if the add-on should hold it.
  Delivered by:
  - **Design-revision pass** ([PR #99](https://github.com/skull-01/script.oppo203.iso.external/pull/99), merge `32ae49c`): the wizard rename so file names / `StepId`/`ScreenId` / components / labels all match the displayed step numbers — **Player = step 2** (`step2.tsx`/`Step2*`), **TV = step 3** (`step3.tsx`/`Step3*`), **HDMI Input = step 4** (`step4.tsx`, replacing `step35.tsx`); `steps.ts` is the source of truth. Plus the design-review pass: reordered/relabeled stepper + chain (ISO Playback → Kodi → Player → TV, gated node removed), centered + animated chain icons, the Step 0 "Ideal preparations" table, the Tier A "SSH can be disabled after setup" note, and **real brand badges** via a new `src/shell/BrandIcon.tsx` drawing CC0 marks from `simple-icons@^16.21.0` (OPPO/Sony/Samsung/LG/Roku/Panasonic render real marks; TCL/Hisense/Vizio aren't in the package → device-glyph fallback). UI/flow only — no Rust/settings/mapping/generate changes. Added the AGENTS.md norm **"Names must match what the user sees."**
  - **Release prep** ([PR #100](https://github.com/skull-01/script.oppo203.iso.external/pull/100), merge `6fa8c76`): bumped `0.1.0 → 0.2.0` across the 3 guarded pins (`package.json` / `Cargo.toml` / `tauri.conf.json`) + lockfiles (`version.test.ts` guard green); `npm run dist` build evidence under `release-evidence/v0.2.0/`.
- **Sony brand-badge white-on-white — FIXED 2026-05-31** ([PR #120](https://github.com/skull-01/script.oppo203.iso.external/pull/120)): light marks now get a
  dark `.brand-logo-mark-dark` chip via a luminance check in `BrandIcon.tsx`; colored marks keep
  the white chip. (Was: white Sony `#FFFFFF` mark invisible on the white `.brand-logo-mark`;
  flagged in PR #99 + the v0.2.0 notes.)
- **Prior config history (unchanged):** `configurator-v0.1.0` first binary (PRs #94/#95, the
  build recipe + evidence; was a public pre-release), wizard wiring (PR #68 + the 16 review
  bugs #72–#87, fixed/merged), the Chinoppo `M9205 V1` split (PR #91 — see §3a), and the
  scaffold stack (#30/#33/#34/#35/#52). See §15 +
  [`configurator/CONFIGURATOR_HANDOFF.md`](configurator/CONFIGURATOR_HANDOFF.md).

- **Resume here next (configurator):**
  1. **Teaching-commentary pass (cross-area, PAUSED mid-flight)** — the configurator's ~17 TS
     files (`configurator/src/**`) are the lighter tail of the same commentary theme. Do the
     **add-on side first** — `external_player.py` is the style gate. **Full exact plan in §3c; when
     proposing this theme, reproduce §3c's verbatim briefing EXACTLY (operator directive).** ← resume here.
  2. **AVR follow-ups — scoped this session, NOT built** (from the naming/AVR audit):
     **PR B** — a configurator `vitest` that pins the two `avr-models.json` copies byte-identical
     + schema invariants (closes the no-guard gap — see [[configurator-avr-db-no-consistency-guard]]);
     **PR C** — a real Step-5 **reachability probe** (TCP-probe the receiver's control port via the
     existing `tv_port_probe`; the operator chose the *real-probe* flavor over mirroring the
     **mocked** TV "mute test" — see [[configurator-control-tests-are-mocked]]). Growing
     `avr-models.json` (both copies identical, bump `db_version`) is the third, data-entry one.
  3. **Install + smoke-test the published `v0.5.0` binary** on a clean Windows machine (MSI + NSIS)
     — launch + icon, the **Step 5 (AV Receiver)** flow incl. the new **Sony PSK/ack/URI card →
     "we'll enable" callout**, the Step 3 region filter, Step 2 facts line — operator action;
     build/unit + browser-preview verified only.
  4. **AVR on-hardware verification (software-verified only).** v0.5.0 + the Sony auto-enable make
     the add-on actually **power on + switch a real receiver** on handoff. All backend/input
     mappings are `validated:false` and the Sony/Pioneer drivers are experimental — confirm against
     a real Denon/Yamaha/Onkyo/Pioneer/Sony. Then the deploy paths (Tier A/B/C) — operator action.

- **Open `area:configurator` issues:** **#103** (TV DB schema v2) and **#105** (canonical players
  DB) — both **delivered in `configurator-v0.3.0`**, SHA-commented, open only **awaiting operator
  Phase-C verify/close** (steps in the checklist). The 16 review bugs **#72–#87** stay **closed**.
  #99/#100/#120–#128 were PR-only themes (no tracked issue), per the configurator's
  untracked-delivery pattern.
