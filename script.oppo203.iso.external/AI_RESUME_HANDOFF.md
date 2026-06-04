# AI_RESUME_HANDOFF.md — session continuity for `script.oppo203.iso.external`

**Audience:** any AI agent (Claude, Cursor, Codex, …) starting or resuming work on this
repo. Read this file **first**. Treat live code + `git`/`gh` output as authoritative; this
file is the map and the memory.

**Repo:** `github.com/skull-01/script.oppo203.iso.external` · **Default branch:** `main`
**Last sync:** `main`@`15640a5` (EOD #21 — **Addon `v2.9.16` AND configurator `v0.9.5` BOTH SHIPPED — operator's 3-theme override (Addon 1 finish-the-ship + Cfg 2 installer-single-prompt + Cfg 3 Phase-C-confirm), completed automatically.** (1) **Finished the v2.9.16 ship:** merged PR [#333](https://github.com/skull-01/script.oppo203.iso.external/pull/333) (`371c5ff`), tagged + published [`v2.9.16` Final](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/v2.9.16) (ZIP 376 KB + SHA256 via `package.yml`), restored **configurator-v0.9.4** as repo "Latest" (the bare add-on tag should not hold it), SHA-commented the 18 folded `area:addon` issues (#221–#224/#226–#233/#235–#237/#254/#256/#275, left OPEN), added a Phase-C checklist row + refreshed `docs/ai-handoff/AI_RESUME_GUIDE.md`. (2) **Cfg installer single old-version prompt** (ENH #334) shipped as **configurator-v0.9.5** across 3 PRs: [#335](https://github.com/skull-01/script.oppo203.iso.external/pull/335) vendor the exact `@tauri-apps/cli` 2.11.2 NSIS template + a drift guard, [#336](https://github.com/skull-01/script.oppo203.iso.external/pull/336) remove the reinstall page (202 lines) + broaden `installer-hooks.nsh` `NSIS_HOOK_PREINSTALL` to remove a prior NSIS *or* MSI install behind one confirmation, [#337](https://github.com/skull-01/script.oppo203.iso.external/pull/337) bump. Tag `configurator-v0.9.5` → CI published MSI/NSIS as **Latest** (bundles add-on v2.9.16). **NSIS template compiled locally with `makensis` (`tauri build --bundles nsis`) on PR1+PR2** because the configurator PR gate does NOT run `tauri build` — only the release tag job does ([[configurator-ci-skips-tauri-build]]). (3) **Cfg Phase-C** confirmed already scripted in the checklist (no gaps). Gate: add-on pytest **1187/3** (serial coverage 99% per the v2.9.16 CI gate — no add-on code changed since); cfg `tsc -b` · **vitest 359** · **cargo 57** · `vite build`. **0 open PRs; working tree clean.** ENH #334 + the 18 addon issues SHA-commented + OPEN (only-operator-closes). **Resume → operator Phase-C on real hardware** (install v2.9.16 zip in Kodi; v0.9.4→v0.9.5 single-prompt upgrade on a Windows host) **or a fresh theme** (cfg i18n migration is the remaining grounded theme). See §3a/§3b.) · `main`@`5fa1b70` (EOD #20 — **add-on `v2.9.16` BUILT + PR [#333](https://github.com/skull-01/script.oppo203.iso.external/pull/333) open, CI GREEN, NOT yet merged/tagged/published.** Operator's **3-theme override** (Addon 2 + Cfg 1 + Cfg 2); `done for the day` called mid-release while CI ran. v2.9.16 folds the 7 post-v2.9.15 fixes (AVR/Pure-HTTP correctness, monitor/transport hardening, schema guards, honest launch, Samsung HDMI, coercion #275/#329); release verification surfaced+fixed a `discovery._safe_port` mypy regression + a cross-area **AutoScript CR/LF injection** in `generate()` (full fix: add-on `_safe_text` + `autoscript-gen.ts` mirror + `crlf_paths` fixture + both consistency guards). Gate: add-on pytest **1187/3** · serial coverage **99%** · mypy **51/0** · ruff clean · audit **607/607**; cfg `tsc -b` · **vitest 357** · `vite build`. Cfg themes 1 (i18n) & 2 (installer single-prompt) grounded but **NOT started**. **Resume → merge PR #333 + tag `v2.9.16` + publish FIRST, then the cfg themes.** See §3a/§3b.) · `main`@`eec9edf` (EOD #14 — **long configurator session off `resume`: shipped v0.8.5 → v0.8.6 → v0.8.7, built the configurator's FIRST CI + tag→release automation, and LOCKED the Developer Options plan as the next theme.** (1) **Reset-all hang fix + live progress** ([#266](https://github.com/skull-01/script.oppo203.iso.external/issues/266)→[#267](https://github.com/skull-01/script.oppo203.iso.external/pull/267)) → **v0.8.5**. (2) Operator "do all of this automatically" → a **7-theme infra/hardening batch → v0.8.6**: repo hygiene ([#271](https://github.com/skull-01/script.oppo203.iso.external/pull/271)); the configurator's **first GitHub Actions CI + `configurator-v*` tag→build+publish** ([#272](https://github.com/skull-01/script.oppo203.iso.external/pull/272) — windows-latest gate; first run caught that tauri `build.rs` needs the bundled add-on zip → gate now runs `bundle:addon`+Python before `cargo test`); dashboard **diagnostics export** ([#273](https://github.com/skull-01/script.oppo203.iso.external/pull/273)); **single-prompt installer** ([#274](https://github.com/skull-01/script.oppo203.iso.external/pull/274)); add-on **property tests** that found+fixed a real `OverflowError` in `http_info_indicates_playing` ([#275](https://github.com/skull-01/script.oppo203.iso.external/issues/275)→[#276](https://github.com/skull-01/script.oppo203.iso.external/pull/276)); **i18n scaffold** ([#277](https://github.com/skull-01/script.oppo203.iso.external/pull/277)); bump #278. (3) **v0.8.7 follow-ups**: **Hisense E8N Pro** TV-DB row + new `hisense-china-android` lineup ([#280](https://github.com/skull-01/script.oppo203.iso.external/pull/280); live to the in-app Update-DB button), **hid the Step 0 "Not yet"** button ([#281](https://github.com/skull-01/script.oppo203.iso.external/pull/281); OPPO NAS path dormant), **TV family Sizes** display ([#282](https://github.com/skull-01/script.oppo203.iso.external/pull/282)), bump #283 → tag → CI-published **configurator-v0.8.7** (holds "Latest", bundles add-on v2.9.15). (4) **OPPO HTTP command catalog** — 61 endpoints, tester-contributed (Darren Solomon) ([#285](https://github.com/skull-01/script.oppo203.iso.external/pull/285)). (5) **Regenerated `docs/BUILD_PLAN.md`** (#286/#287) + **LOCKED the Developer Options console plan** as the queued next configurator theme (#288 → §3b ▶ NEXT THEME: PR A shell + PR B-OPPO first). **Releases are now `git tag configurator-v*` → CI** ([[configurator-release-is-manual]] updated). All **software-verified**; Phase-C = operator on real hardware. Memory: [[gh-powershell-json-gotchas]] extended (a PowerShell here-string mangles `gh --body`/`git -m` → use `--body-file`/`-F`). **Resume → Configurator → Developer Options (PR A + PR B-OPPO).** See §3b.) · `main`@`f437567` (EOD #13 — **#263 Reset-all reachability SHIPPED + cut configurator `v0.8.4` (holds the repo "Latest").** Operator: `resume` → Configurator → **#263** (the queued theme), then **"go"** (build) + **"go"** (ship). Fixed that the **Reset all configurations** action rendered only on the post-setup Live dashboard (reachable only from the final test screen) — invisible on a fresh/broken install: new `reset_all` screen (`configurator/src/screens/ResetAll.tsx`) reusing `ResetAllCard` **unchanged**, surfaced from a persistent app-header "Reset all…" button (every screen, hidden only on the reset screen) + a Step 0 "Reset all configurations…" link; `steps.ts` adds `reset_all` to `ScreenId` + both exhaustive maps (`SCREEN_TO_STEP`→`step0`, `SCREEN_TO_CHAIN`→`media`); new pure `steps.test.ts`. PR [#264](https://github.com/skull-01/script.oppo203.iso.external/pull/264) (`285b5e3`, merged `473df58`) → bump v0.8.4 PR [#265](https://github.com/skull-01/script.oppo203.iso.external/pull/265) (merged `f437567`) → release **configurator-v0.8.4** (MSI 3,682,304 B + NSIS 2,542,219 B + SHA-256, unsigned, bundles add-on v2.9.15, holds "Latest"). Gate: tsc 0 · **304 vitest** (+3 `steps.test.ts`) · vite build · tauri release build; **browser-verified** the nav end-to-end (no console errors). #263 SHA-commented + **OPEN** (only-operator-closes); Phase-A/C checklist row added. **Phase-C only:** the reachability entries + the on-box reset (unchanged from v0.8.2) on real hardware — operator. See §3b.) · `main`@`49972f5` (EOD #12 — **Full-audit remediation + TV-DB growth + reset-all + installer old-version check; cut configurator v0.8.1/v0.8.2/v0.8.3.** Operator ran a **full audit** (7 read-only agents over addon + configurator) then directed automatic execution: **all 30 findings fixed + merged** across 7 PRs (#225/#234/#238/#245/#253/#255/#257 — addon A1/A2/A3/H2/L12 + configurator C1/C2), ~27 `type:bug` issues filed + SHA-commented + **OPEN**. Then **TV DB +110 TCL/Hisense rows** (#258, 350→460), the **Reset-all-configurations** action (#260 — deletes the add-on + every configurator-deployed file from the box per tier, then resets the configurator to first-run), and an **installer old-version check** (#262 — NSIS PREINSTALL hook offers to remove all old versions before installing). **Three configurator releases** via manual `npm run dist` — **v0.8.1 / v0.8.2 / v0.8.3** (v0.8.3 holds the repo "Latest"; all bundle add-on v2.9.15, unsigned, software-verified only). Standing rule saved: a bare "release" = the **configurator** release bundling the add-on. Gate: addon pytest **1155/3** · serial coverage 99% · mypy --strict 51/0 · ruff clean; configurator tsc 0 · **301 vitest** · cargo · vite build. **Phase-C hardware + installer validation is the only remaining work.** See §3a/§3b.) · `main`@`be196ac` (EOD #11 — **Xnoppo V3 / Pure-HTTP-436 SHIPPED: built + merged all 6 PRs and cut stable add-on `v2.9.15` + configurator `v0.8.0` (configurator holds the repo "Latest"; bundles v2.9.15, confirmed in the MSI).** Operator: "save the plan, run all the PRs automatically, cut stable release", with 4 front-loaded decisions (merge-all-to-main / flip-default-to-Pure-HTTP / authorize-8-settings / cut-stable). Delivered the 7th preset `http_handoff_http` (asymmetric `http` monitor), pure-HTTP launch orchestration (mount + ISO auto-heal + confirm), checkfolderhasBDMV-first disc nav, selectable HDMI switching, and the Pure-HTTP default flip — **all best-effort + capability-gated so the six prior presets stay byte-identical** (build18 order guard green). PRs #208/#210/#212/#214/#216/#218; ENH #207/#209/#211/#213/#215/#217 SHA-commented + **OPEN** (only-operator-closes). Gate on the v2.9.15 cut: pytest **1132/3** · serial coverage **99%** · mypy `--strict` **51/0** · audit **598/598** · CI Release gate green. Two memory gotchas saved: [[serial-only-monkeypatch-target]] (passes `-n auto`, fails the serial gate) + [[xnoppo-v3-pure-http-shipped]] (the 3-place asymmetric preset contract). **Phase-C hardware validation is the only remaining work.** See §3a/§3b + `docs/XNOPPO_V3_ADOPTION_AND_DECISION_TREE_ENHANCEMENTS.md`.) · `main`@`c200349` (EOD #10 — **shipped add-on `v2.9.14` + configurator `v0.7.0` (both stable; configurator holds the repo "Latest" badge), then planned + SAVED the Pure-HTTP/436 initiative (PRs 1–6) to `docs/BUILD_PLAN.md` and queued it as the next theme.** Merged the 7-PR cfg queue #200–#204 (stale #165/#166 closed); add-on cut via `/release`+`package.yml`, configurator via a manual `npm run dist` build ([[configurator-release-is-manual]]); open for operator close: cfg #167/#168/#103/#105. See §3a/§3b + `docs/BUILD_PLAN.md`.) · `main`@`d1fe1dc` (EOD #9 — **resume → "do all cfg": grounded (#103/#105 found already-shipped → evidenced for close), built the dashboard-memory stack #200→#201→#202, plus #203 shared preset source / #204 TV DB China-CN models / build-plan refresh / fullwired audit; 6 draft PRs queued, 0 merged, all software-verified only.** #103 (TV DB v2, 324 models) + #105 (players DB) were found **already implemented on `main`** → evidence-commented + checklist note (`516d465`), ready for operator close. Dashboard memory rebuilt on the current dashboard (stale #165/#166 superseded): [#200] appdata store (Rust `read/write_app_json` + `safe_app_rel`) → [#201] #167 settings-snapshot diff card → [#202] #168 session-history card with **exact `session_id` dedup** (the 5.1 unlock). [#203] shared `playback-presets.json` + Python parity guard `test_playback_presets_consistency.py` + `presetsdb.ts` (kills the manual `CANONICAL_SIX` mirror; no runtime change). [#204] TV DB **324→350** (+26 China TCL/Hisense under a new **`CN`** region — FFALCON 雷鸟 + Hisense VIDAA, all `validated:false`/low; browser-verified the CN pill) + a stale `tv_ip` comment fix. `docs/BUILD_PLAN.md` refreshed (`d1fe1dc`, initiative software-complete). **Fullwired audit** confirmed configurator↔add-on is fully software-wired (43 emitted keys all read; architecture keys read from the runtime `settings.xml`; 32 Tauri cmds live). **Phase-C hardware validation is the only remaining work.** Open issues: #44 (addon), #103/#105/#167/#168 (cfg — all implemented, ready to close). See §3a/§3b.) · `main`@`2a4e4af` (EOD #8 — **built + MERGED ALL of guided-install Phases 3/4/5 (13 PRs), fully wired the configurator↔add-on, and cleared the manual-verification queue**: operator drove "build all of Phases 3/4/5, full auth, merge as I go, finer PRs, file ENH issues" off `resume`. Foundation #174/#175 merged first; then the **backend layer (4 PRs)** — Phase 3.1 AVR switch [#177] + TV switch [#179], Phase 4.1 `oppo_power` [#181], Phase 5.1 add-on richer `oppo203iso-status.json` [#183]; then the **UI layer built by 3 parallel sub-agents in worktrees (7 PRs)** — 3.2/3.3 step5 switch-and-verify + auto-find [#184/#188], 4.2/4.3/4.4 OPPO self-test (Rust `copy_to_share` + live SVM3 + orchestration) [#185/#187/#190], 5.2/5.3 dashboard consume-richer-status + TV liveness + full-chain [#186/#189]. Then operator: **"close the verification queue (keep the checklist)" + "fully wire everything"** → closed **23** confirmation-queue issues (this session's ENH + the already-merged prior addon backlog #111–#117/#123/#150–#152/#113/#173), KEPT `docs/MANUAL_VERIFICATION_CHECKLIST.md`; audited (**all 32 Tauri commands UI-wired, zero dead, no functional stubs**) + fixed the one real gap — **full TV-backend config persistence** [#198/#199] (`mapping.ts` now writes `sony_psk` / adb keyevent shells / lg·samsung·custom `{tv_ip}` commands / smartthings token+device+inputs+ack), so the add-on can drive every TV backend. **Combined-`main` gate green: `tsc` / 261 vitest / `vite build` / `cargo` 37 / addon 1046·3 / mypy 51·0 / coverage 99%. ALL software-verified ONLY — only operator Phase-C hardware validation remains (nothing is blocked).** Left open by design: #167/#168 (PRs #165/#166 unmerged + now CONFLICTING vs the rebuilt dashboard), #103/#105 (DB backlog), #44 (tester-solicitation umbrella). See §3a/§3b.) · `main`@`7554c15` (EOD #7 — **merged the guided-install initiative to `main` + built Phase 1b NAS-path capture (#174) + resolved D-2/D-3 + built D-3 (#175)**: operator drove a long configurator build off `resume`. **Merged #170/#171/#172 → `main`** via the experimental3 integration branch (`b927b33`; all show **MERGED**; configurator now **0.6.0** on `main`; gate green `cargo`/`tsc`/**180 vitest**/`vite build`). Built **Phase 1b** NAS-path capture (observe-and-verify, D-4, issue **#173**) as draft **[#174](https://github.com/skull-01/script.oppo203.iso.external/pull/174)** — `kodi_now_playing` (Kodi JSON-RPC over SSH), `oppo_http_play` (activate→signin→`/playnormalfile`, **pulled forward from Phase 4 PR-4.1**, no new crate), pure `deriveRewrite`/`parseOppoPlayingPath`, `oppo_playback_info` (best-effort `/getmovieplayinfo`), + the OPPO media-path capture card on the Player step (`step2.tsx`) with a manual **SMB/NFS** fallback; gate **cargo 18 / 190 vitest** / `tsc` / `vite build`; **browser-verified** card renders + `deriveRewrite` preview (`smb://10.0.1.10/`→`MyNAS/`) + persist. Resolved **D-2** (user-supplies ISO + placeholder wiring) + **D-3** (Kodi JSON-RPC `Addons.SetAddonEnabled` + manual-restart fallback) in `docs/BUILD_PLAN.md`; built **D-3** as draft **[#175](https://github.com/skull-01/script.oppo203.iso.external/pull/175)** (`kodi_set_addon_enabled` + `apply.ts` Tier-A wiring; cargo **11** / 180 vitest). **Everything software-verified ONLY — hardware-pending** (SSH/UDP/TCP I/O, the OPPO activate+signin+play handshake, whether `/getmovieplayinfo` carries the path). **Resume: build PR-4.2** (D-2 test-ISO copy, placeholder) on the #175 branch; then review/merge #174 + #175.) · `main`@`1c81f2c` (EOD #6 — **guided-install initiative**: turned the configurator into a guided installer+monitor across 4 branches — Phase 1 install, Phase 2 SSH-first flow + de-stub + TV IP (browser-verified), Phase 3 Roku ECP switch, + an integration — and shipped pre-releases **configurator-v0.6.0-experimental2** + **experimental3** and add-on **v2.9.14-experimental**; opened **3 draft PRs #170/#171/#172**; merged the six-preset matrix guard **#169** + its norm; refreshed `docs/BUILD_PLAN.md`. **Everything software-verified ONLY — no hardware validated install/OPPO-play/switch; `main` code lines (add-on v2.9.13, configurator v0.5.0) untouched.**) · **Prior:** `main`@`b098fd4` (EOD #5 — configurator dashboard follow-on; **2 draft PRs** [#165](https://github.com/skull-01/script.oppo203.iso.external/pull/165)/[#166](https://github.com/skull-01/script.oppo203.iso.external/pull/166) + **2 ENH** #167/#168; `main` code unchanged; **0 merged**) · **2026-06-01 (EOD #5, latest) — Dashboard follow-on (Configurator theme 3): a 2-PR "dashboard memory" stack + matching ENH issues; software-verified only, nothing merged.** Operator picked **Configurator theme 3**, then **"go"** + **"file the matching"**. Built [#165](https://github.com/skull-01/script.oppo203.iso.external/pull/165) `9b15e93` **settings-snapshot diff** (a *Configuration changes* card: a Snapshot-now button reads the box's `settings.xml` via a new shared `fileReadPlan(state, rel)` factored from `statusReadPlan`, parses via a new exported `parseSettingsXml` factored from `mergeSettingsXml`, **masks secret ids** `sony_psk`/`smartthings_token`/`sony_avr_psk`→`[secret]` via the shared `debug/log.ts` `isSensitiveKey`, persists the sanitized snapshot + diffs vs the prior one; new Rust `read_app_json`/`write_app_json` — a `safe_app_rel`-guarded appdata JSON store modelled on `save_wizard_state`) → [#166](https://github.com/skull-01/script.oppo203.iso.external/pull/166) `1408eab` **historical session log** (a *Session history* card: a new pure `session_log.ts` `foldObservation` folds the add-on's overwritten `oppo203iso-status.json` into a persisted, deduped, capped-50 history, reusing #165's appdata store; **heuristic dedup** — the `_status` schema has no session id/start-time, so identical back-to-back sessions can't be split, exactness would need an addon-area schema field, out of scope). Filed ENH **#167**/**#168** (`area:configurator`), SHA-commented + left **open** (only-operator-closes); checklist Phase A/C rows added. Gate on the PR-166 tip (incl. #165): `tsc --noEmit` 0 / **194 vitest** (+19: settings_diff 5, parseSettingsXml 4, fileReadPlan 3, session_log 7) / `cargo test` **8** (+3 `safe_app_rel`) / `vite build`; **addon `resources/` untouched → suite stays 1045/3**; **no new crate dep**; frozen guards (`mergeSettingsXml` `/refusing to overwrite/`, `statusReadPlan` routing, `redact`) held, pinned by their existing tests. ⚠️ **Merge order:** retarget #166 to `main` *first* (`gh pr edit 166 --base main`) before merging #165 — this repo does NOT auto-retarget ([[stacked-pr-local-merge-status]]). · **2026-06-01 (EOD #4) — ALL outstanding drafts MERGED (7 PRs, both areas); 0 open PRs.** Operator picked Configurator **theme 1** + **addon Phase C**, then **"Merge all".** Configurator **Live Session Dashboard** merged bottom-up: D1 [#158](https://github.com/skull-01/script.oppo203.iso.external/pull/158) `5755184` → D2 [#164](https://github.com/skull-01/script.oppo203.iso.external/pull/164) `e4118c0` → D3 [#160](https://github.com/skull-01/script.oppo203.iso.external/pull/160) `e8d35bf`. **Mechanics casualty:** D1's `--delete-branch` **auto-CLOSED** stacked child [#159](https://github.com/skull-01/script.oppo203.iso.external/pull/159) (this repo does NOT auto-retarget) → recovered as new **[#164](https://github.com/skull-01/script.oppo203.iso.external/pull/164)** (identical D2). Addon **issue-audit** stack merged docs-only by retargeting children to `main` first (zero closures): [#161](https://github.com/skull-01/script.oppo203.iso.external/pull/161) `fdd3368` / [#162](https://github.com/skull-01/script.oppo203.iso.external/pull/162) `a543615` / [#163](https://github.com/skull-01/script.oppo203.iso.external/pull/163) `e957aab` (Phase-C runbook now on `main` in `docs/audit/`). Configurator **wire-transcripts** [#153](https://github.com/skull-01/script.oppo203.iso.external/pull/153) `832b76e` — resolved a checklist union conflict + a **duplicate `mod tests`** Rust collision (`cargo check` green but `cargo test` caught `E0428`; folded to one 5-test module). Configurator gate green (`tsc` 0 / **175 vitest** / `cargo check` 0 / `cargo test` 5 / `vite build`); addon `resources/` untouched → suite stays **1045/3**. **Phase C (operator hardware) pending** across the dashboard (esp. D3 dual-subscriber), #153 wire panel, and the SVM3/http_handoff/robustness backlog. **Two merge-mechanics lessons recorded** ([[stacked-pr-local-merge-status]] + [[rust-duplicate-mod-tests-on-merge]]). · **2026-06-01 (EOD #3, prior) — Configurator Live Session Dashboard built + a pure-agent addon issue audit, both as draft stacks (NOTHING merged; code baseline still `72c84d8`).** Operator picked Configurator **Theme 2** → 3 stacked draft PRs: [#158](https://github.com/skull-01/script.oppo203.iso.external/pull/158) device liveness (reuses `tcp_probe`/`oppo_query`; Kodi/OPPO/AVR; TV omitted — no persisted IP), [#159](https://github.com/skull-01/script.oppo203.iso.external/pull/159) current-session panel (reads `oppo203iso-status.json` via the existing SSH/SMB read commands; `parseOppoStatus`), [#160](https://github.com/skull-01/script.oppo203.iso.external/pull/160) gated live verbose stream (new Rust `LiveMonitor` `std::thread` → `oppo-live` events; **dual-subscriber gate** `canStartLiveStream` + auto-stop; no new crate). Gate: `tsc` 0 / **173 vitest** / `cargo check`+`test` 2 / `vite build`. Then operator directed a **pure-agent addon issue audit** → 3 stacked draft PRs [#161](https://github.com/skull-01/script.oppo203.iso.external/pull/161)/[#162](https://github.com/skull-01/script.oppo203.iso.external/pull/162)/[#163](https://github.com/skull-01/script.oppo203.iso.external/pull/163): per-issue ground-truth audit + Phase-C runbook (`docs/audit/`) — **all confirmed fixed in code** (#111/#112/#114–#117/#123 robustness; #150/#151/#152 SVM3) **except #113 partial** (svm3 confirms playback; legacy hold-only). Docs only (empty code diff); cited tests re-run **93 passing**; `ruff format` clean. **6 draft PRs open, 0 merged** — merge each stack **bottom-up** ([[stacked-pr-local-merge-status]]). Phase C still pending on all addon work + D3 dual-subscriber (hardware-unverifiable in-session). · **2026-06-01 (EOD #2) — SVM3 stack MERGED + `http_handoff` six-option shipped + wire-transcripts draft.** Merged all 7 SVM3 stacked PRs (#143–#149) to `main`, filed ENH #150/#151/#152, then built + merged the six-option **`http_handoff`** routing (#154/#155/#156/#157 — addon presets+launch reusing the existing OPPO HTTP fns, configurator pill+payload; gate green: addon 1045/3 cov 99% mypy 51/0, configurator 158 vitest+build). Opened wire-transcripts **draft #153**; planned a live-dashboard Theme 2 (not started). `http_handoff` path-translation is operator/Phase-C; mount endpoints deferred; not hardware-validated. · **2026-06-01 (EOD, prior) — SVM3 four-option playback architecture: planned + built BOTH sides as 7 stacked DRAFT PRs (none merged; `main` code unchanged at `1a1aae6`).** Operator handed in `FOUR_OPTION_PLAYBACK_ARCHITECTURE_SVM3_BUILD_PLAN_BUNDLE.zip`, approved a canonical-format plan, then directed "complete full session A" + "complete session B." **Addon Session A** (review/merge #143→#144→#145): `playback_monitor_mode` + four-option preset (`settings_reader`, reader-only) [[#143](https://github.com/skull-01/script.oppo203.iso.external/pull/143) `cbae76e`]; `OppoSvm3PlaybackMonitor` — a `#SVM 3` verbose-mode monitor that confirms playback/progress from `@UPL`/`@UTC` [[#144](https://github.com/skull-01/script.oppo203.iso.external/pull/144) `3b63054`]; shared `run_playback_session()` both entry points delegate to + split-truth `oppo203iso-status.json` [[#145](https://github.com/skull-01/script.oppo203.iso.external/pull/145) `d5ba5ab`]. Gate up to **1036/3**, coverage 99% (new modules 100%), mypy `--strict` 51/0, ruff clean. **Configurator Session B** (review/merge #146→#147→#148→#149): new **Step 3 "Playback mode"** + renumber TV/HDMI/AVR→4/5/6 [[#146](https://github.com/skull-01/script.oppo203.iso.external/pull/146) `df4012c`]; SVM3-vs-Legacy choice emitting the consistent `playback_architecture(_preset)` + `playback_monitor_mode` triple [[#147](https://github.com/skull-01/script.oppo203.iso.external/pull/147) `5d24d5f`]; SVM3 capability probe in the player test (reuses `oppo_query`, no Rust change) [[#148](https://github.com/skull-01/script.oppo203.iso.external/pull/148) `27c01d2`]; final-test status split + SVM3 honesty note [[#149](https://github.com/skull-01/script.oppo203.iso.external/pull/149) `2dfa86c`]. `tsc -b` + up to **155 vitest** + `vite build` green. **No code on `main`** (all draft); **operator to file 3 `area:addon` ENH issues**; the new settings key was authorized in-session; SVM3 **not** hardware-validated. Phase A/C rows for all 7 in the checklist. See §3a / §3b. · **Prior — 2026-05-31 (EOD) — DB growth + developer debug view (configurator):** operator picked `resume` → Configurator theme 1, then directed AVR-DB growth, TV-DB growth, a planned **developer debug view**, and a final **merge all**. **4 configurator PRs merged to `main`** — [#139](https://github.com/skull-01/script.oppo203.iso.external/pull/139) dedicated Step-5 receiver **restore-input field** (new `state.avrKodiInput` → `avr_restore_input`, replacing the TV `kodiInput` reuse; blank ⇒ non-fatal skip; `type="string"` so no add-on change), [#140](https://github.com/skull-01/script.oppo203.iso.external/pull/140) **AVR DB +15** `validated:false` 2026 model rows (`db_version`→`2026.05.31-avr-2018-2026`), [#141](https://github.com/skull-01/script.oppo203.iso.external/pull/141) **TV DB +28** `validated:false` 2026 rows **+ a NEW `tv_db_consistency.test.ts`** two-copy guard the TV DB lacked, [#142](https://github.com/skull-01/script.oppo203.iso.external/pull/142) **developer debug view** (`src/debug/log.ts` redacting ring buffer + `src/ipc.ts` `invoke` wrapper migrating all call sites + global docked `DebugPanel.tsx`; **Ctrl+Shift+D**, off by default; secrets redacted). All DB rows `validated:false` (**operator fact-check**). Merged locally (`--no-ff`); checklist Phase-A rows union-merged; one `step5.tsx` import conflict resolved (keep `isAvrChain` + route `invoke` via `../ipc`). **Post-merge `main`@`9419bea` green (software-only):** configurator `tsc --noEmit` + `vite build` + **146 vitest**; **addon untouched** (configurator + docs only) → stays **976/3**. **No add-on code change.** **0 open PRs.** See §3b. · **Prior — 2026-05-31 (EOD) — AVR follow-ups + two-chains session (configurator):** operator picked `resume` → **AVR follow-ups**, then directed **merge everything** and a new **two-playback-chains** theme. **8 configurator PRs merged to `main` this session** — AVR follow-ups: [#134](https://github.com/skull-01/script.oppo203.iso.external/pull/134) `avr_db_consistency.test.ts` (pins the two `avr-models.json` copies byte-identical + schema invariants — closes the no-guard gap), [#135](https://github.com/skull-01/script.oppo203.iso.external/pull/135) Step-5 receiver **reachability probe** (reuses the generic `tv_port_probe`; Denon 23 / Yamaha 80 / Onkyo·Pioneer 60128; Sony+custom show no probe). Then **merge everything** landed the 5 prior addon robustness drafts **#129–#133** to `main` (the 7 `type:bug` fixes — `ruff format` CI red now clean). Then the **two-playback-chains** theme: [#136](https://github.com/skull-01/script.oppo203.iso.external/pull/136) Step-0 chain picker + `state.topology` (`kodi_tv_player` | `kodi_avr_tv_player`), [#137](https://github.com/skull-01/script.oppo203.iso.external/pull/137) topology-aware flow + chain viz (Receiver node; Step-4 receiver wording; pure helpers `isAvrChain`/`chainNodeIds`/`step4NextScreen`), [#138](https://github.com/skull-01/script.oppo203.iso.external/pull/138) mapping writes the AVR-switcher settings (`avr_power_on_enabled` + `avr_restore_enabled`/`avr_restore_input` from the Step-4 Kodi input; `tv_switching_enabled` gated off in the AVR chain). **Soft default** (null topology ⇒ TV chain; both chains keep escape hatches). **Software-verified only** — configurator `tsc -b` + `vite build` + **123 vitest** green; addon **976 pass / 3 skip**, ruff check + `ruff format --check` clean. **No add-on code change** — every emitted setting already exists in `settings.xml` and is read by `avr_control.py`. Phase-A/C rows added per PR; **operator closes the 7 bugs after Phase-C** (PRs are merged but the issues stay OPEN per only-operator-closes). **0 open PRs.** See §3b. · **Prior — 2026-05-31 (EOD) — naming-consistency + draft-merge session:** merged **9 PRs** to `main` — configurator: Sony brand-badge fix ([#120](https://github.com/skull-01/script.oppo203.iso.external/pull/120)), v0.5.0 Step-5 verification checklist entry ([#121](https://github.com/skull-01/script.oppo203.iso.external/pull/121)), **Sony AVR auto-enable** ([#122](https://github.com/skull-01/script.oppo203.iso.external/pull/122) — captures PSK+ack+input-URI so Sony enables like the other backends), and a **naming-consistency sweep** (`oppoInput`→`playerInput` [#124](https://github.com/skull-01/script.oppo203.iso.external/pull/124); `players.json`→`players-models.json` [#125](https://github.com/skull-01/script.oppo203.iso.external/pull/125); `CONFIGURATOR_HANDOFF` map [#127](https://github.com/skull-01/script.oppo203.iso.external/pull/127); new `docs/NAMING_CONVENTIONS.md` + historical flags [#128](https://github.com/skull-01/script.oppo203.iso.external/pull/128)); addon: **TV backend modules renamed `tv_*`** for parity with `avr_` ([#126](https://github.com/skull-01/script.oppo203.iso.external/pull/126)), and the two prior-session drafts landed — **read-only OPPO status probe** ([#118](https://github.com/skull-01/script.oppo203.iso.external/pull/118)) + **functional-flow diagrams** ([#119](https://github.com/skull-01/script.oppo203.iso.external/pull/119)). Filed `type:bug` **[#123](https://github.com/skull-01/script.oppo203.iso.external/issues/123)** (pre-existing `ruff format` drift on 3 test files — the only CI "Lint and format" red). **0 open PRs.** · **Configurator `v0.5.0` shipped + published as the repo's GitHub "Latest"** — an **AVR (AV receiver) feature in two releases**: `v0.4.0` added an **AVR control database** (224 AV-receiver/processor **model families** 2018–2025 across 10 brands — Denon/Marantz/Yamaha/Onkyo/Pioneer/Integra/Sony/Anthem/Arcam/NAD — schema v2, the TV-DB twin) + a typed `avrdb.ts` loader + an **optional Step 5 (AV Receiver)** picker + 18 vitest ([PR #109](https://github.com/skull-01/script.oppo203.iso.external/pull/109) merge `6251cdf`); then `v0.5.0` **wired Step 5 into the add-on `settings.xml`** (`avrAddonBackend()` maps DB→add-on enum: Pioneer→`pioneer_eiscp`, Sony→`sony_audio_api` configured-but-off, custom_command no-op; conservative `avr_control_enabled`; Receiver-control card captures IP + player input) for true TV/Player parity ([PR #110](https://github.com/skull-01/script.oppo203.iso.external/pull/110) merge `bc3ad0e`). Published **`configurator-v0.5.0`** (MSI 3,174,400 B + NSIS 2,071,403 B + SHA-256, unsigned, software-verified only; published assets re-downloaded byte-identical). **No add-on code change** — like the TV DB, the AVR DB isn't loaded by the add-on at runtime, and the add-on already shipped the AVR settings + guarded drivers → no add-on release. Repo-wide "Latest" sits on `configurator-v0.5.0` (flip to add-on `v2.9.13` with `gh release edit v2.9.13 --latest` if desired). · **Tests on `main`@`be196ac`:** addon **1132 passed, 3 skipped** (coverage 99%; mypy `--strict` 51/0; ruff check + `ruff format --check` clean; audit_release **598/598**); configurator **294 vitest + `tsc --noEmit` 0 + `vite build` + `cargo` OK** (the only non-green CI check is the known-broken `claude-review` bot; the prior `ruff format` drift #123 was resolved + closed) · **Still pending (prior session, untouched):** teaching-commentary Step 2 (`external_player.py`, comments-only) checkpointed as `wip:` `62b22eb` on branch `claude/teaching-comments-extplayer-r3k8m2x9` (pushed, **not** on `main`), awaiting the operator's Step-2 style sign-off (§3a/§3c)
**Latest release (2026-06-03):** configurator **`configurator-v0.9.5`** ([configurator-v0.9.5](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.9.5), **holds the repo "Latest"**; installer **single old-version prompt** via a vendored `@tauri-apps/cli` 2.11.2 NSIS template — ENH #334, PRs #335/#336/#337; NSIS setup.exe 2,625,487 B + MSI 3,788,800 B + SHA256SUMS, CI-built on the tag, bundles add-on v2.9.16; software-verified, single-prompt upgrade UX is **Phase-C**). Add-on **`v2.9.16` Final** is **published** ([v2.9.16](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/v2.9.16), tag `v2.9.16`; ZIP 376,051 B + SHA256 via `package.yml`; folds the post-v2.9.15 AVR/Pure-HTTP correctness, monitor/transport hardening, schema guards, honest launch, Samsung HDMI, coercion #275/#329, + AutoScript CR/LF fixes) — the bare add-on tag is intentionally **not** "Latest" (the configurator holds it). _Prior:_ configurator **`configurator-v0.9.4`** (held "Latest" until v0.9.5; see §3b for the v0.9.0→v0.9.4 chain). _Prior:_ configurator **`configurator-v0.8.7`** ([configurator-v0.8.7](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.7), then held "Latest"; **built + published by the new CI** on the `configurator-v0.8.7` tag — hides the Step 0 "Not yet" button (#281), adds the TV-step family **Sizes** display (#282), and bundles the updated TV DB incl. the **Hisense E8N Pro** (#280, also live to the in-app Update-DB button); MSI 3,694,592 B + NSIS 2,556,655 B + SHA-256, unsigned, bundles add-on v2.9.15, software-verified only, Phase-C-pending). _Prior:_ configurator **`configurator-v0.8.6`** ([configurator-v0.8.6](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.6); the **7-theme infra/hardening batch** — the configurator's **first GitHub Actions CI + tag→release automation** (#272), dashboard diagnostics export (#273), single-prompt installer (#274), i18n scaffold (#277), repo hygiene (#271), + an add-on `OverflowError` fix (#275/#276); the **first CI-built+published** release; MSI 3,694,592 B + NSIS 2,549,305 B + SHA-256). _Prior:_ configurator **`configurator-v0.8.5`** ([configurator-v0.8.5](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.5); **Reset-all hang fix + live progress** — a fast reachability pre-probe so the reset no longer freezes on an unreachable device, box + local resets run as separate stages, and a live step list (#266/#267); manual `npm run dist` — the CI did not exist yet; MSI 3,690,496 B + NSIS 2,549,305 B + SHA-256). _Prior:_ configurator **`configurator-v0.8.4`** ([configurator-v0.8.4](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.4), held "Latest" until v0.8.5; makes the **Reset all configurations** action reachable from a persistent app-header entry (visible on every screen) + the Step 0 gate via a new `reset_all` screen that reuses `ResetAllCard` unchanged — issue #263 / PR [#264](https://github.com/skull-01/script.oppo203.iso.external/pull/264), fixing that the reset previously rendered only on the post-setup dashboard; MSI 3,682,304 B + NSIS 2,542,219 B + SHA-256, unsigned, bundles add-on v2.9.15, software-verified only — reachability browser-verified, the on-box reset path unchanged from v0.8.2 and **Phase-C-pending**; manual `npm run dist`, see [[configurator-release-is-manual]]). _Prior:_ configurator **`configurator-v0.8.3`** ([configurator-v0.8.3](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.3); adds an **installer old-version check** — the NSIS setup detects any previously-installed version (our NSIS install + any MSI install of the product) and offers one prompt to remove all old versions before installing (PR #262); bundles add-on v2.9.15; MSI 3,682,304 B + NSIS 2,540,337 B + SHA-256, unsigned, software-verified only — **installer detect/remove not hardware-validated** (makensis compiled the hook into the installer; runtime is Phase-C); manual `npm run dist`, see [[configurator-release-is-manual]]). _Prior:_ configurator **`configurator-v0.8.2`** ([configurator-v0.8.2](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.2); adds the **Reset-all-configurations** action — a confirm-gated dashboard button that deletes the add-on + every file the configurator copied to the Kodi box (per deployed tier: SSH for A / SMB-local for B / nothing for C) and resets the configurator to first-run (PR #260, bump #261); bundles add-on v2.9.15; MSI 3,686,400 B + NSIS 2,539,158 B + SHA-256, unsigned, software-verified only — **on-box deletion not hardware-validated**; manual `npm run dist`, see [[configurator-release-is-manual]]). _Prior:_ configurator **`configurator-v0.8.1`** ([configurator-v0.8.1](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.1); bundled add-on v2.9.15 + the 2026-06-02 **audit-remediation fixes** (Waves A1/A2/A3 + H2 + L12 add-on; C1/C2 configurator) **+ 110 new TCL/Hisense TV-DB rows** (2018–2026, 350→460); MSI 3,674,112 B + NSIS 2,535,740 B + SHA-256, unsigned, software-verified only — **Phase-C hardware validation pending**; manual `npm run dist`, see [[configurator-release-is-manual]]). The audit remediation merged 7 PRs (#225/#234/#238/#245/#253/#255/#257) clearing all 30 findings of the 2026-06-02 full audit; the TV-DB add is PR #258; the v0.8.1 bump PR #259. _Prior:_ add-on **`v2.9.15`** ([v2.9.15](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/v2.9.15), tag `v2.9.15`) + configurator **`configurator-v0.8.0`** ([configurator-v0.8.0](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.8.0); bundled add-on v2.9.15) — the **Xnoppo V3 / Pure-HTTP-436 initiative SHIPPED** (PRs 1–6: 7th preset `http_handoff_http`, the `http` playback monitor, pure-HTTP launch orchestration, checkfolderhasBDMV-first disc nav, selectable HDMI switching, flipped Pure-HTTP default; every new HTTP/mount/BDMV/HDMI step is best-effort + capability-gated so the six prior presets stay byte-identical; software-verified only, **Phase-C hardware validation pending**). Add-on cut via `/release` + `package.yml` (gate pytest **1132/3** · serial coverage **99%** · mypy `--strict` **51/0** · audit **598/598**); configurator via manual `npm run dist` (MSI 3,682,304 B + NSIS 2,538,677 B + SHA-256, unsigned). ENH #207/#209/#211/#213/#215/#217 open for operator close. See [[xnoppo-v3-pure-http-shipped]] / [[serial-only-monkeypatch-target]]. _Prior:_ add-on **`v2.9.14`** ([v2.9.14](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/v2.9.14), PR #205 → merge `a6fdcef`) + configurator **`configurator-v0.7.0`** ([configurator-v0.7.0](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/configurator-v0.7.0), PR #206 → merge `e55a947`, **holds the repo "Latest" badge**). **v2.9.14 Final** is the first stable add-on release since v2.9.13: six-option playback architecture (SVM3 + http_handoff), the `#SVM 3` verbose-mode monitor, richer `oppo203iso-status.json` session status, robustness hardening (`tcp_qpl_poll` default, bounded holds, sentinel self-heal); `runtime_behavior_changed: true`; gate pytest **1053/3** · coverage **99%** · mypy --strict **54/0** · ruff clean · audit **589/589** · CI Release gate green; cut via the `/release` skill + `package.yml`. **configurator-v0.7.0** promotes the 0.6.0/0.7.0 line (guided installer + live dashboard — Phases 1–5, dashboard-memory, AVR/TV/players DBs, shared preset guard) to stable and **bundles add-on v2.9.14** (verified inside the MSI); MSI 3,674,112 B + NSIS 2,527,350 B + SHA-256, unsigned, software-verified only; **manual build** (`npm run dist` → MSI/NSIS + `gh release create` — there is no configurator CI/release workflow; see [[configurator-release-is-manual]]). Prior latest (held the badge until 2026-06-02): configurator **`configurator-v0.5.0`** — **wired the AVR Step 5 selection into the add-on's
`settings.xml`** (`avr_backend`/`avr_host`/`avr_player_input` + conservative `avr_control_enabled`;
Pioneer→`pioneer_eiscp`, Sony→`sony_audio_api` configured-but-off, Anthem/Arcam/NAD no-op), giving
Step 5 parity with the TV/Player steps; [PR #110](https://github.com/skull-01/script.oppo203.iso.external/pull/110) merge `bc3ad0e`; MSI 3,174,400 B + NSIS 2,071,403 B
+ SHA-256, unsigned, software-verified only (published assets re-downloaded + verified
byte-identical). Prior: **`configurator-v0.4.0`** — the **AVR control database** (224 AV-receiver
model families 2018–2025, the TV-DB twin) + the optional Step 5 picker ([PR #109](https://github.com/skull-01/script.oppo203.iso.external/pull/109) merge `6251cdf`);
and `configurator-v0.3.0` (TV DB v2 + players DB). · **Issue model:** **hybrid** — GitHub Issues for
bug/enhancement tracking, PRs for delivery; every issue tagged `area:addon` or
`area:configurator`.

**What this is:** A Python 3.9+ Kodi add-on (`script.oppo203.iso.external`) for OPPO 203/205
and compatible-clone external-player handoff, plus a new Tauri 2 + React/TS Windows
**configurator** under [`configurator/`](configurator/) that sets the add-on up (writes
`playercorefactory.xml` + the remote-bridge keymap, probes the TV/player, captures HDMI
inputs).

**Deep-archive companion** (historical builds, not the spine):
[`docs/ai-handoff/AI_RESUME_GUIDE.md`](docs/ai-handoff/AI_RESUME_GUIDE.md) and the
`Combined_AI_Handoff_*` build-reconstruction files.

---

# §1 The `resume` command

Work in this repo is split into **two areas** that share one machine and one git history:

- **Addon** — the Kodi add-on (Python under `resources/`, entry points `default.py` /
  `service.py`, release tooling under `tools/`, tests under `tests/`).
- **Configurator** — the Windows configurator app (Tauri 2 + React/TS under
  `configurator/`).

Issues are tagged with **`area:addon`** or **`area:configurator`** labels so the resume
command can summarize each area independently. Both areas live on `main`; one environment
serves both (see §2a).

When the operator types **`resume`** (alone), do exactly this:

1. **Read this file** (especially §3a "Addon work in progress" and §3b "Configurator work
   in progress") and the repo instruction files
   ([`AGENTS.md`](AGENTS.md), [`CLAUDE.md`](CLAUDE.md), [`CONTRIBUTING.md`](CONTRIBUTING.md)).
2. **Run the unified environment readiness check** in §2a — it covers prerequisites for
   **both** areas (Python venv + dev deps for addon; Node + Rust + Tauri + WebView2 for
   configurator; plus the `area:addon` / `area:configurator` GitHub labels). Print a small
   readiness table.
   - All rows green → one line `Environment: ready ✓ (addon + configurator)` and continue.
   - An *auto-repo* row missing → install it (idempotent: `venv`, `pip install`, `npm
     install`, `gh label create --force`), re-check, report what was installed.
   - An *auto-system* row missing → attempt `winget install ... --silent
     --accept-source-agreements --accept-package-agreements` (per row), re-check; on
     success continue, on failure print the manual fix and **STOP**.
   - A *manual* row missing → print the exact fix command and **STOP**.
3. **Report recent backlog activity per area.** Two parallel blocks, **Addon** then
   **Configurator**, each with:
   - *Last 5 issues created* — `gh issue list --label area:<area> --limit 5 --state all
     --sort created` — one line each as `#N <short title snippet>` (operator's "list
     issues with titles" norm).
   - *Last 5 issues closed* — `gh issue list --label area:<area> --limit 5 --state closed
     --sort updated` — same formatting.
   - *Work in progress* — paraphrase §3a (for addon) or §3b (for configurator) in 2–4
     lines: the in-flight branch/PR, what's done, what's left, blockers.

   If any issues exist that carry neither `area:addon` nor `area:configurator`, list them
   under a short **Unclassified** tail (≤5 rows) so they can be triaged.
4. **Suggest themes per area, separately** (still one theme = one session per §4).
   - **Addon — 1–3 candidate themes**, each one line, leading with any unfinished §3a
     entry.
   - **Configurator — 1–3 candidate themes**, each one line, leading with any unfinished
     §3b entry.

   **STOP and wait** for the operator to pick **one area and one theme** before doing any
   new work. Do not start work in both areas in the same session (§4 session-shape rule).

## Other natural-language triggers any agent must honor

| Trigger | Behavior |
|---|---|
| **`done for the day`** | Run §2 fully. |
| **`confirmation queue`** | List open issues whose implementing SHA was commented (per §17a / the "only operator closes" norm) but which the operator hasn't verified/closed yet. |
| **`bugs`** | `gh issue list --label type:bug --state open` — format each row as `#N <title snippet>`. |
| **`enhancements`** | `gh issue list --search "ENH- in:title" --state open` — same formatting. |
| **`backlog audit`** | Report from §17a cache first; ask before re-scanning live GitHub state (per operator norm #10). |
| **`build plan`** | Show contents of [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) (create as stub on first use). |
| **`refresh the build plan`** | Regenerate `docs/BUILD_PLAN.md` from live open issues. |
| **`plan`** / **`create a plan`** / **`scope this`** | Produce a plan in the **canonical Plan format** ([`AGENTS.md`](AGENTS.md) → "Plan format"): ground against the current code first (confirm `file:line` anchors, flag already-done work), then **theme → per-PR scope blocks → dependency chain → 📊 rollup → ⚠️ risk callouts → verification regime → ✅ Go / 🛑 Wait / 🔁 Replan**. STOP for a Go before building. |
| **`dev note: <text>`** | Append `<text>` VERBATIM (dated, no editing, no summarizing) to §20. |
| **`update AI_RESUME_HANDOFF.md`** | Run the maintenance recipe at the end of §2. |
| **`protocol 1`** (full auth) | Operator grants full auth to run a theme end-to-end incl. merge + release. Batch ALL decisions up front (one `AskUserQuestion`), then execute uninterrupted. Hard rules still apply. See §4 + [[protocol-1-full-auth-autonomous]]. |

Slash-command equivalents: `/resume`, `/done-for-the-day`, `/release`.

---

# §2 The `done for the day` command

When the operator types **`done for the day`**, do exactly this:

1. **Push ALL current work to the active branch.** No work left only on this machine.
   - Tests green → normal commit + `git push -u origin <branch>`.
   - Tests red or work mid-flight → `wip: <short summary>` checkpoint commit + push. Note
     the wip status in §3 so next session knows it's not done.
2. **Update §3 "Work in progress" — overwrite §3a and §3b independently.** Touch only the
   area(s) you actually worked in this session. For each touched area: current state,
   what's in flight, the clean stopping point for tomorrow, any blockers. If you didn't
   touch an area, leave its subsection unchanged. If an area ended clean, write `(none)`
   in its subsection so next `resume` reports it as a fresh slate.
3. **Append a dated entry to §19** "Updates to this document" — one bullet per material
   change (this entry, plus anything new added during the session).
4. **Refresh the §17a backlog audit cache** if any issues were opened, closed, or
   meaningfully retitled this session.
5. **Commit + push the handoff** — `docs: end-of-day handoff <YYYY-MM-DD>` on `main` if
   you have direct-to-main rights for docs-only changes, otherwise via short-lived PR.
6. **End-of-day summary** — 2-4 lines: what shipped today, what's open, what to pick up
   first tomorrow. Do **NOT** start new feature work.

Maintenance recipe (for `update AI_RESUME_HANDOFF.md`): refresh §3, §17a; append §19; if
substantive Q&A happened, append §21; verify §2a still matches the actual readiness check.

---

# §2a Environment readiness

The readiness check verifies the **single Windows machine** can edit, test, and build
**both** areas — the Kodi add-on (Python) **and** the Tauri 2 configurator (Node + Rust +
WebView2). One pass covers both.

**Tiers.** `auto-repo` = idempotent and runs in user scope, the resume command does it
without prompting. `auto-system` = the resume command attempts `winget install` (best
effort, no admin elevation requested; user-scope installs don't need it); on success it
re-checks and continues, on failure it prints the manual fix and **STOPS**. `manual` = an
operator action the resume command will not perform (auth flows, browser-redirect installs).

| Row | Prereq | How to check (PowerShell) | Tier | Install command |
|---|---|---|---|---|
| 1 | **git** ≥ 2.30 | `git --version` | auto-system | `winget install --id Git.Git -e --silent --accept-source-agreements --accept-package-agreements` |
| 2 | **`gh` CLI** authenticated | `gh auth status` | manual | `gh auth login` (operator approves the browser flow) |
| 3 | **Python** 3.9+ on PATH | `python --version` | auto-system | `winget install --id Python.Python.3.12 -e --silent --accept-source-agreements --accept-package-agreements` |
| 4 | Repo **`.venv`** | `Test-Path .venv` | auto-repo | `cd C:\Users\rigel\Documents\gitrepo\script.oppo203.iso.external; python -m venv .venv` |
| 5 | **Python dev deps** | `.venv\Scripts\python.exe -m pytest --version` | auto-repo | `cd C:\Users\rigel\Documents\gitrepo\script.oppo203.iso.external; .venv\Scripts\python.exe -m pip install -r requirements-dev.txt paramiko` |
| 6 | **paramiko** (SSH probes) | `.venv\Scripts\python.exe -c "import paramiko"` | auto-repo | covered by row 5 |
| 7 | **Node** 20+ | `node -v` | auto-system | `winget install --id OpenJS.NodeJS.LTS -e --silent --accept-source-agreements --accept-package-agreements` |
| 8 | **npm** 10+ | `npm -v` | bundled | comes with Node row 7 |
| 9 | configurator **`node_modules`** | `Test-Path configurator\node_modules` | auto-repo | `cd C:\Users\rigel\Documents\gitrepo\script.oppo203.iso.external\configurator; npm install` |
| 10 | **Rust toolchain** 1.77+ | `cargo --version; rustc --version` | auto-system | `winget install --id Rustlang.Rustup -e --silent --accept-source-agreements --accept-package-agreements; rustup default stable` |
| 11 | **MSVC Build Tools** (Tauri linker) | `(Get-Command link.exe -ErrorAction SilentlyContinue) -ne $null` or `cd configurator; npm run tauri info` | auto-system | `winget install --id Microsoft.VisualStudio.2022.BuildTools -e --silent --accept-source-agreements --accept-package-agreements --override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"` (multi-GB; first run is slow) |
| 12 | **WebView2 runtime** | `Test-Path 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}'` | bundled-w11 | bundled with Windows 11; if absent: `winget install --id Microsoft.EdgeWebView2Runtime -e --silent --accept-source-agreements --accept-package-agreements` |
| 13 | **Configurator icon** (placeholder OK) | `Test-Path configurator\src-tauri\icons\icon.ico` | auto-repo | generate from a placeholder PNG via `cd configurator; npm run tauri icon -- ../docs/installuidraft/.../placeholder.png` (or commit a stub `icon.ico`); blocks `cargo build` otherwise |
| 14 | Repo has **`area:addon`** and **`area:configurator`** labels | `gh label list --json name --jq '.[].name' \| Select-String '^area:(addon\|configurator)$'` returns both | auto-repo | `gh label create area:addon --color 0E8A16 --description "Kodi add-on (Python)" --force; gh label create area:configurator --color 5319E7 --description "Windows configurator (Tauri 2)" --force` |

**PATH gotcha on Windows after row 10 installs:** the cargo bin dir
(`$env:USERPROFILE\.cargo\bin`) is NOT on the inherited PATH of fresh `PowerShell` tool
calls until a shell restart. Prefix every cargo invocation in the same session as the
install with `$env:PATH = "$env:USERPROFILE\.cargo\bin;" + [Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH","User"); `
or call cargo by full path.

Rows are checked in order; a missing row at any tier is acted on per its tier rule
described above. There is no database; no external services to verify. (Memory note
`tauri-env-installed` records that rows 10/11 already passed on 2026-05-29; row 13 was
satisfied by PR #35 merging the icon stub at `12e5b18`.)

---

# §3 Work in progress (resume here first)

> **Read this FIRST on `resume`.** §3a covers Addon work, §3b covers Configurator work.
> Maintained by `done for the day` — each subsection is overwritten independently. If a
> subsection is empty (`(none)`), that area ended clean; offer the operator a fresh theme
> in that area.

## §3a Addon work — in progress

**As of 2026-06-04 (player-DB enrichment — Protocol 1 run; add-on `v2.9.17` Final SHIPPED + published; clean slate).**
**Clean stopping point — no addon work in flight; `main`@`4d553d8` (v2.9.17 + the cfg v0.9.7 bump merged); 0 open PRs; add-on suite 1219/3, serial coverage 99% (5922 stmts), mypy --strict 51/0, ruff clean, audit_release PASS 616/616.**
Operator invoked **Protocol 1** ([[protocol-1-full-auth-autonomous]]) — full auth to run a theme end-to-end + release with all decisions batched up front. Built (umbrella ENH [#341](https://github.com/skull-01/script.oppo203.iso.external/issues/341)) and shipped **add-on v2.9.17**: five OPPO-clone player variants (M9205 V2/V3/V4 → mirror M9205, M9702 Plus → M9702, VenPro V203 → new `venpro` family → CineUltra), appended to the `oppo_hardware_model` enum + wired end-to-end across the registries via the M9205-V1-split template, plus a **cross-area Dolby Vision data layer** — new `resources/lib/oppo/dolby_vision.py` (`DOLBY_VISION_PROFILES` + `DOLBY_VISION_TV_RULE`, normalized enums) mirrored by `dolby_vision` fields + `global_dv_rule` in `players-models.json`, pinned both ways by `test_players_db_consistency.py`. New tests: `test_clone_variants_split.py`, `test_dolby_vision_capability.py`. Capability summary vendored at `docs/configurator/players-db/PLAYBRIDGE_CAPABILITY_SUMMARY.md`. Feature PR [#342](https://github.com/skull-01/script.oppo203.iso.external/pull/342) (`7633b0f`) → standalone **v2.9.17** release PR [#343](https://github.com/skull-01/script.oppo203.iso.external/pull/343) (merge `4a23f16`, tag `v2.9.17` published; ~73-file bump + 8-doc evidence). **New norm this session (operator-flagged):** the README front-page **Current status** + **Current release** must be refreshed every release (they'd gone stale at v2.9.16 / cfg-v0.8.5) — now pinned by `tests/test_readme_current_release.py` ([[readme-current-status-per-release]], AGENTS.md, §4). ENH #341 SHA-commented + **OPEN**; all player rows `validated:false`, DV/clone stances research-sourced, hardware validation not claimed. **Resume (addon): Phase-C** the new clone variants + Dolby Vision guidance on real hardware (the v2.9.17 checklist row), or the teaching-commentary pass (§3c, paused).

---

**As of 2026-06-03 (EOD #21 — add-on `v2.9.16` Final SHIPPED + published; clean slate).**
**Clean stopping point — no addon work in flight; `main`@`15640a5`; 0 open PRs; add-on suite 1187/3 (`-n auto` re-run locally this session; serial coverage 99% per the v2.9.16 CI gate — no add-on code changed since).**
The operator's 3-theme override opened with **Addon 1 = finish the v2.9.16 ship** (the EOD #20 mandated first action). Done end-to-end: merged PR [#333](https://github.com/skull-01/script.oppo203.iso.external/pull/333) (`371c5ff`) → tagged + pushed **`v2.9.16`** → `package.yml` published [v2.9.16 Final](https://github.com/skull-01/script.oppo203.iso.external/releases/tag/v2.9.16) (`script.oppo203.iso.external-2.9.16.zip` 376,051 B + `.sha256`) → set the release title/notes from `docs/release-history/RELEASE_NOTES_v2.9.16.md` → **restored configurator-v0.9.4 as repo "Latest"** (publishing the add-on tag auto-grabbed it; the configurator holds "Latest" by convention, and a bare add-on zip as "Latest" would misdirect Windows users). **Bookkeeping:** SHA-commented the 18 folded OPEN `area:addon` issues (#221–#224, #226–#233, #235–#237, #254, #256, #275) as "shipped in v2.9.16" — **left OPEN** (only-operator-closes; #329 was already closed); added the v2.9.16 Phase-C row to `docs/MANUAL_VERIFICATION_CHECKLIST.md`; refreshed `docs/ai-handoff/AI_RESUME_GUIDE.md` (latest-release facts → v2.9.16, the now-passing `claude-review` note, a 2026-06-03 state block). **No add-on runtime code changed this session** — the v2.9.16 content was already on the merged branch. **Resume (addon): Phase-C the v2.9.16 release on real hardware** — install the published zip in Kodi (verify SHA-256), confirm it loads + shows v2.9.16; the folded runtime fixes' device verification is the per-issue runbook in [`docs/audit/`](docs/audit/README.md) + the AVR/Pure-HTTP/monitor checklist rows. Operator on-device; no agent code. Or the teaching-commentary pass (§3c, paused, awaiting Step-2 sign-off).

---

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

## §3b Configurator work — in progress

**As of 2026-06-04 (player-DB enrichment — Protocol 1 run; configurator `v0.9.7` SHIPPED; bundles add-on v2.9.17; holds "Latest").**
**Clean stopping point — no configurator work in flight; `main`@`4d553d8`; 0 open PRs; cfg gate green (`tsc -b` · vitest 361 · `cargo test` on CI · vite build).**
Configurator side of the **Protocol 1** player-DB run (§3a, ENH [#341](https://github.com/skull-01/script.oppo203.iso.external/issues/341)): the players DB (`players-models.json` ×2) gained the 5 clone variants + a `venpro` family + per-model `dolby_vision` blocks + a top-level `global_dv_rule`, with `playersdb.ts` types — the Step-2 picker + `mapping.ts` surface them automatically (**no UI code changed**). Shipped as **configurator v0.9.7** (bump PR [#344](https://github.com/skull-01/script.oppo203.iso.external/pull/344) merge `4d553d8` → tag `configurator-v0.9.7`; CI built MSI/NSIS + published as Latest, bundling the v2.9.17 add-on). **Branding fix:** `configurator-ci.yml` now titles releases **"Kodi Oppo External Player Configurator v\<version\>"** (was the stale generic "Configurator \<tag\>" that lagged the v0.9.6 rebrand); `configurator-v0.9.6` was retitled to match. **Deferred follow-up (operator CI-time question):** one reviewed CI-optimization PR — skip `claude-review` + the add-on `ci.yml` jobs on configurator-only / `release/*` PRs, and skip the configurator `gate` job on tag pushes (the tag's release job recompiles anyway) — to cut the ~5–6 min claude-review + ~4.5 min windows gate off release wall-clock (the ~8 min MSI/NSIS build is unavoidable). **Resume (configurator): Phase-C** v0.9.7 on a real Windows host (brand + upgrade from v0.9.6 + bundled add-on reports v2.9.17), the **CI-optimization follow-up**, or **i18n migration** (the still-queued grounded theme).

---

**As of 2026-06-03 (EOD #21 — installer single old-version prompt SHIPPED as configurator `v0.9.5`; clean slate).**
**Clean stopping point — no configurator work in flight; `main`@`15640a5`; 0 open PRs; cfg gate green (`tsc -b` · vitest 359 · cargo 57 on CI · vite build); `configurator-v0.9.5` holds the repo "Latest".**
The 3-theme override's **Cfg 2 = installer single old-version prompt** (the grounded EOD #20 theme 2). An upgrade used to risk **two** old-version prompts (Tauri's built-in NSIS reinstall page + our PREINSTALL hook). Shipped as **3 CI-gated PRs** under ENH [#334](https://github.com/skull-01/script.oppo203.iso.external/issues/334):
- **PR [#335](https://github.com/skull-01/script.oppo203.iso.external/pull/335)** (`d460c6b`) — **vendor** the exact `@tauri-apps/cli` 2.11.2 `installer.nsi` into `configurator/src-tauri/installer.nsi` (verbatim + version stamp) and set `bundle.windows.nsis.template`; new `src/installer-template.test.ts` **drift guard** pins the stamp to the resolved CLI version in `package-lock.json`. Behavior-neutral.
- **PR [#336](https://github.com/skull-01/script.oppo203.iso.external/pull/336)** (`920f740`) — **remove the reinstall page** (`PageReinstall` / `PageReinstallUpdateSelection` / `PageLeaveReinstall` + the `Page custom` insertion — 202 lines) and **broaden** `installer-hooks.nsh` `NSIS_HOOK_PREINSTALL` to detect+remove a prior **NSIS** install (its `UninstallString`, silent `/S _?=<dir>`) in addition to the parallel-**MSI** case → one `MB_YESNO` covers both. Known relaxation: the silent-install (`/S`) downgrade auto-abort (depended on the removed page) is now inert; GUI installs unaffected.
- **PR [#337](https://github.com/skull-01/script.oppo203.iso.external/pull/337)** (`342ee0d`) — bump 0.9.4→0.9.5 + `configurator/release-evidence/v0.9.5/BUILD_NOTES.md`.
Tag `configurator-v0.9.5` → CI `release` job built MSI/NSIS + published as **Latest** (NSIS 2,625,487 B + MSI 3,788,800 B + SHA256SUMS; bundles add-on v2.9.16). **Key gotcha (saved to memory [[configurator-ci-skips-tauri-build]]):** the configurator PR gate runs only `tsc`/`vitest`/`cargo test` — it does **NOT** run `tauri build`, so the NSIS template is first compiled by `makensis` only on the `configurator-v*` tag. I therefore compiled it **locally** (`tauri build --bundles nsis`) on PR1 and PR2 before merging — both produced a working `*-setup.exe`. ENH #334 SHA-commented + **OPEN**; v0.9.5 Phase-C row in the checklist. **Resume (configurator): Phase-C the single-prompt upgrade on a real Windows host** (install v0.9.4 → run v0.9.5 → confirm exactly one prompt + settings survive; smoke a fresh install → no prompt; optional MSI-present case). Or the remaining grounded theme: **i18n migration** (theme 1 — ~660 raw strings across ~32 files onto the `t()` scaffold, 4-PR slice; see the EOD #20 block below).

---

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

## §3c Active cross-area theme — teaching-commentary pass (Step 2 written — awaiting style sign-off)

**As of 2026-05-30 (later — teaching-commentary session; operator picked this theme on `resume`).**
**Step 1 (repo + real end-to-end flow map) DONE; Step 2 now WRITTEN and checkpointed, awaiting the
operator's style sign-off.** `resources/lib/kodi/external_player.py` was commented to the bar
(module docstring + numbered end-to-end flow + import-shim note + beginner docstrings on every
previously-undocumented function + one trick-play gloss), comments/docstrings only — committed as
`wip:` `62b22eb` on branch `claude/teaching-comments-extplayer-r3k8m2x9` (pushed; **not** on `main`,
**not** merged). Backstop green (`ruff` clean; suite 943/3). The exact plan is saved here so a
future session resumes it verbatim. **This theme intentionally INVERTS the repo's default
"no inline comments / don't state the obvious" norm** (AGENTS.md → *No inline code comments by
default*) — it is operator-directed for one specific reader (see mandate). Honor it for this
theme only; the default norm still governs all other work.

### The mandate (operator brief — faithful)
- **Reader:** a near-beginner — almost no coding experience, no AV / playback-pipeline
  background. The commentary is his **only** window into the system. Goal: after reading it he
  can understand the system well enough to **spot bugs and propose better process flows**. So
  **explain what a developer would find obvious** — but put the teaching in **docstrings +
  block comments**, NOT a comment on every line; the code must stay readable underneath. Define
  jargon inline the first time it appears (playercorefactory.xml, "external player",
  `setResolvedUrl`, listitem, manifest/HLS/DASH, ADB/ECP/eISCP/PSK…) — one short clause each.
- **Make the flow legible (the most important part):** trace the REAL end-to-end path in THIS
  codebase and document it in **numbered plain English** at the top of the entry point and/or
  the playback-pipeline file, naming the functions/files at each step. At every handoff explain
  WHAT is passed to the next stage and WHAT that stage ASSUMES it is receiving — bugs and
  better-flow ideas live in those handoffs/assumptions.
- **Quality bar:** module docstring per file (what it's responsible for + where it sits in the
  chain); function/class docstrings (plain what / in / out / what can go wrong / side effects —
  especially Kodi/AV ones: shows a dialog, talks to the player, reads/writes settings, hits the
  network, starts a stream); make assumptions + fragile points explicit ("breaks if X changes",
  "assumes the stream is always HLS", "this is a timeout in seconds — too low and slow
  connections fail"); document the non-obvious-but-intentional (AV/Kodi quirks, magic numbers,
  ordering deps — "looks redundant but Kodi needs it because…"); weight heaviest on the playback
  chain + entry points, lighter on trivial helpers; match the existing docstring style, else
  Google-style.
- **Hard constraints:** comments + docstrings ONLY — no logic changes, no renames, no refactors,
  no reformatting/reflow, no reindent of untouched lines, no reordering. The diff is **added
  comments, nothing else.**
- **Suspect discipline:** found a bug / dead code / confusing flow while reading? **DON'T fix** —
  add it to a running list with a plain-English why, and show the operator at the end. Keep the
  commentary commits clean.

### The process (operator's 3 steps)
1. **Map the repo + the real flow** — show structure, flow, and the best first file. ✅ DONE
   (saved below).
2. **Comment ONE playback-chain file** to the bar above (including its place in the flow), then
   **STOP and show the diff** — wait for style sign-off ("written for a non-coder, taught from
   the comments alone") before touching anything else. First file =
   `resources/lib/kodi/external_player.py` — **✅ DONE this session** (commented + diff shown
   in-session; `wip:` `62b22eb` on `claude/teaching-comments-extplayer-r3k8m2x9`, pushed, awaiting
   the operator's style sign-off). **← RESUME at that sign-off**, then go to Step 3.
3. After style approval, work in **small reviewable batches** (a module or a few related files),
   **show the diff before each commit**, commit messages `docs: add commentary to <module>`,
   and **do NOT push** — the operator reviews and pushes.

### Resume briefing — reproduce VERBATIM when proposing this theme on `resume`

**Operator directive (2026-05-30):** when `resume` proposes this theme, do **not** paraphrase or
summarize it — **reproduce the briefing inside the fenced block below exactly as written** (omit
only the outer ```` ```` fence; the content already carries its own headings, code block, and
table). This is the canonical Step-1 pitch the operator signed off on. (Working detail — mandate,
process, resume steps — is above/below; this block is the operator-facing text.)

````md
I have the full map now — three subsystem agents plus my own read of the spine (`addon.xml`, `default.py`, `service.py`, `external_player.py`). Here's **Step 1**, then I'll answer your time question.

## Repo structure (grouped, ~49 addon modules + ~17 configurator)

```
default.py        ← add-on menu + remote-key bridge entry (xbmc.python.script)
service.py        ← background service: startup auto-power + (optional) interception (xbmc.service)
resources/lib/
  kodi/   external_player.py ★ (the pipeline), installer.py (builds routing file),
          intercept.py + disc_classification.py (is-this-a-4K-disc?),
          playercorefactory_merge.py, settings_reader.py (config+hardware map),
          diagnostics.py, preset_manager.py, i18n.py, logging/version/…
  oppo/   oppo_control.py ★ (TCP/HTTP protocol core), oppo_tcp_client.py (verbose-push),
          oppo_remote.py (remote-key→command), nas_playback_adapter.py, discovery.py,
          command_map.py, constants.py, hardware_{capabilities,profiles,presets}.py, …
  tv/     tv_control.py (dispatcher) + adb/roku_ecp/sony/smartthings/command backends
  avr/    avr_sequence.py (flow glue) + avr_control.py (factory) + denon/onkyo/yamaha/sony
configurator/src/ … Tauri/React wizard (TS) — generates the same files from Windows
```
★ = the load-bearing playback-chain files.

## The real end-to-end flow (what actually happens)

**Important:** this add-on does **not** stream or use `setResolvedUrl`. "Playback" = handing a physical OPPO Blu-ray player a disc to play over the LAN, while Kodi just holds the slot. There are **two architectures** (setting `playback_architecture`); both converge on `external_player.py`.

**Setup (one-time):** Kodi → `default.py` → `installer.main()` → pick architecture → generate `playercorefactory.xml` + remote keymap into `addon_data/generated/`, copy into Kodi's `userdata/`.

**Play-time — External Player mode (default):**
1. User plays a disc file (`.iso`/BDMV/`.mpls`) whose **filename carries a 4K tag** (`4K`/`UHD`/`2160p`).
2. **Kodi's own playercorefactory engine** (not add-on code) matches the generated `<rule filetypes="iso/bdmv/mpls" filename=".*(4K|UHD|2160p…).*">` and launches `<player name="Oppo203ISO">` → runs `external_player.py --addon-data <dir> --file "<file>"` as a subprocess.
3. `external_player.main()` (`external_player.py:321`):
   - a. `read_settings()` → b. optional `run_preflight()` (TCP `#QPW`/`#QIS`) → c. `mark_session_active()` writes the `oppo203iso-active` sentinel.
   - d. **`fast_start()` — order is TV → AVR → OPPO**, each *non-fatal*: `switch_to_oppo()` (tv_control→adb/sony/roku) flips the TV's HDMI input → `pre_playback_sequence()` (avr_sequence, off by default) → `run_start()` (oppo_control): Wake-on-LAN, `#SVM` verbose mode, then send `oppo_start_commands` over TCP:23 (`#PON`, or `#EJT` for clones) **or** the HTTP-API path (UDP `0x55`→:436 wake, signin, `/playnormalfile`).
   - e. **`hold_playback()`** — occupy the Kodi slot until the OPPO reports stop, via `http_poll` / `tcp_qpl_poll` (`#QPL`) / `verbose_push` (`@UPW`/`@UPL` via oppo_tcp_client) / `manual_file` / `fixed_timeout`.
   - f. **`fast_return()`** (finally) — `oppo_stop_commands` → AVR restore → switch TV back to Kodi → g. `clear_session_active()`.
4. **During playback**, remote keys: keymap maps Kodi buttons → `RunScript(default.py, oppo_key, <key>)` → `oppo_remote.send_remote_key()` → 76-key command map → TCP:23 (audio/subtitle/seek fall back to HTTP).

**Play-time — Service Interception mode (diverges at steps 1–3):** `service.py` holds an `InterceptionPlayer`; on play, `onAVStarted` → `_handle_started` reads `getPlayingFile()` → `should_intercept_4k_disc_source()` (tag AND disc-style) → **stops Kodi's player** → threads into the *same* `fast_start → hold_playback → fast_return`. (Service mode also wakes the player at Kodi startup via `_kodi_startup_power_on`.)

## Recommended first file to comment: **`resources/lib/kodi/external_player.py`**

It *is* the playback pipeline — both architectures converge here, so it's the right home for the numbered flow overview, and it's the hardest documentation case (the TV/AVR/OPPO handoffs, the 5-mode `hold_playback` state machine, the "non-fatal by design" invariants, and the magic timeouts). If a non-coder can follow the system from this file's comments, the style is proven. `oppo_control.py` (the protocol core) is the natural **second**.

## Preliminary suspect list (tracking; full version at the end — not fixing any)
- **Dead-at-runtime code:** `intercept.py` whitelist/blacklist API, `playercorefactory_merge.py`'s safe-merge engine, `nas_playback_adapter.trigger_nas_playback`, `oppo_tcp_client.wait_for_stop_persistent` — tested but no production caller.
- **Real bug-smell:** `default.py` diagnostics `_http` probe checks **port 80**, but the OPPO HTTP API is **port 436**.
- **`#POW` toggle not filtered when already-on** → could power the player *off* (`oppo_control._filter_commands_for_mode`).
- **4 overlapping hardware/model registries**, only `settings_reader` drives runtime; an unknown/typo'd model fails *open* to stock `#PON` (wrong for a clone needing `#EJT`).
- **TV defaults ON** (`adb`→`192.168.1.60`) but AVR defaults OFF; AVR powers on at start but never powers off (`avr_power_off_enabled`/`avr_volume_automation_enabled` have no consumer).
- **Clone-wake logic duplicated** in `oppo_control` + `oppo_remote`; **no-op smartthings branch** in `tv_control._switch`; **XML regex vs substring-tag** drift.

---

## ⏱️ Time estimate (your question)

Two honest framings — my hands-on work vs. wall-clock (which your review cadence drives, not my typing speed):

| Phase | Files | My focused work |
|---|---|---|
| **Step 2** — `external_player.py` solo + diff for your style sign-off | 1 | **~10–15 min** (next thing I do) |
| Core playback chain — `oppo_control`, `service`, `oppo_tcp_client`, `oppo_remote`, `intercept`+`disc_classification`, `installer`, `settings_reader`, `default` | ~11 | ~4–5 h (these carry the teaching weight; `oppo_control`/`installer` are big) |
| OPPO support — discovery, command_map, constants, nas_adapter, path_mapper, hardware_* | ~10 | ~1.5 h |
| TV subsystem | ~7 | ~1 h |
| AVR subsystem | ~9 | ~1.5 h |
| Kodi support — diagnostics, logging, i18n, preset_manager, version… | ~10 | ~1 h |
| Configurator (TS) | ~17 | ~1.5–2 h |

- **Total:** ~**15–18 reviewable batches**, **~10–13 hours** of my focused generation, weighted heavily to the ~12 core files (trivial helpers go in minutes).
- **Wall-clock:** gated by your reviews. Same-day batch reviews → ~**3–5 working sessions**. The **Step-2 style sign-off is the pacing item** — everything after it inherits that template, so once you approve the `external_player.py` style, the rest moves fast.
- **Backstop per batch** (no push): `ruff check`/`ruff format --check` + the source-introspection-sensitive tests (`test_chinoppo`, `build8`) so added docstrings never break the suite; configurator gets `tsc`/`vitest`.
````

### Resume instructions
On `resume`, if the operator (re)picks this theme: re-read this §3c and **reproduce the verbatim
briefing above exactly** (operator directive — no paraphrase). **Status: Step 2 is already
written** for `resources/lib/kodi/external_player.py` (`wip:` `62b22eb` on
`claude/teaching-comments-extplayer-r3k8m2x9`, pushed, **awaiting the operator's style sign-off**).
So: (a) if the operator **approves the style**, retitle that file's commit to `docs: add commentary
to kodi.external_player` and continue Step 3 in small batches — **next file `oppo_control.py`** (the
protocol core) — showing the diff before each commit and **not pushing** (the operator reviews and
pushes); (b) if the operator **wants style changes**, revise `external_player.py` first, re-show the
diff, and re-gate. **Do NOT push/merge the wip branch unprompted.** Suspect found in Step 2 (not
fixed): `hold_playback`'s `verbose_push` failure path sets `mode='tcp_qpl_poll'` but that branch
sits above it, so the fallback silently degrades to `fixed_timeout` (default 180 min) instead of
QPL-polling. The subagent subsystem maps that informed this (OPPO control / Kodi routing / TV+AVR)
live in the 2026-05-30 post-EOD session transcript.

---

# §4 Build norms

- **Session shape — one theme per session, soft cap ≤ 4 PRs.** Mixing themes within a
  session is where bugs slip in (proven in retros). If the operator nudges into a second
  theme, suggest finishing the current one and resuming next session.
- **Plans are deliverables, not sketches.** Any plan request (or any multi-PR theme)
  follows the **canonical Plan format** in [`AGENTS.md`](AGENTS.md): ground against the
  current code first (`file:line` anchors, flag already-done work), then theme → per-PR
  scope blocks (each with anchors + a `Tests:` line) → dependency chain → 📊 rollup →
  ⚠️ risk callouts → verification regime → **✅ Go / 🛑 Wait / 🔁 Replan**. Don't start
  building until the operator says Go.
- **No inline code comments by default.** Add only when the WHY is non-obvious (subtle
  invariant, workaround for a specific bug). Never explain WHAT — identifiers do that.
- **Lint/test backstop** — `pytest -n auto` + `ruff check .` must pass before promoting a
  PR out of draft. For configurator changes: `npx tsc --noEmit && npm run build` too.
- **Six-preset matrix is a maintained contract** — the add-on is **one package with six
  runtime presets** (3 routing × 2 monitor), **not** six builds (`docs/BUILD_PLAN.md` D-C).
  Any change to playback routing/monitor logic must keep all six working **on both sides**
  and exercise all six — they share one dispatch (`resources/lib/kodi/playback_session.py`),
  so a fix to one path can silently break another. The six are a cross-area contract:
  add-on `PLAYBACK_ARCHITECTURE_PRESETS` (`resources/lib/kodi/settings_reader.py`) ↔
  configurator `mapping.ts`. See the **"six playback-architecture presets are a maintained
  matrix"** norm in [`AGENTS.md`](AGENTS.md); guards: `tests/test_architecture_presets.py`
  (`PresetConsistencyGuard`, iterates all six), `tests/test_playback_session_modes.py`,
  `configurator/src/mapping.test.ts`.
- **Honest signature** — claim only what was actually run in this session. "Code compiles"
  ≠ "feature works". Distinguish typecheck / unit-tested / clicked-through / verified by
  operator. Never weaken the project's
  **"software-verified / hardware validation not claimed"** wording.
- **Scope discipline** — don't refactor adjacent code. Don't add features, abstractions,
  fallbacks, or validation the task doesn't require. Smallest possible diff.
- **Test link norm** — every completed change ends with one copy-paste line (run command
  or unittest command) + URL.
- **Only the operator closes issues** — never `gh issue close`, never `Closes #N`. Comment
  the SHA on the issue and add a verification step to
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md).
- **README front-page status is part of every release.** The hand-written **Current status**
  blurb + **Current release** table in `README.md` live *outside* the `render_docs` generated
  block, so `render_docs --write` does NOT touch them — and they went stale (lagged at add-on
  v2.9.16 / configurator v0.8.5 while Latest was v0.9.6). Refresh them on **every release**:
  the add-on version / build / runtime-ZIP **and** the configurator's new **Latest** tag, plus
  `Runtime behavior changed` / `Hardware validation claimed`. Pinned by
  `tests/test_readme_current_release.py` (add-on fields); the configurator line is
  norm-enforced. See AGENTS.md + [[readme-current-status-per-release]].
- **Protocol 1 (full-auth autonomous run).** When the operator invokes it, batch ALL decisions
  the run needs up front (one `AskUserQuestion`), then execute the theme end-to-end — build →
  gate → merge → release → record — **uninterrupted**. Hard rules still apply (never close
  issues, never touch operator-only/secret files, honest signature, the cross-area guard
  contracts). See [[protocol-1-full-auth-autonomous]].

---

# §5 Architecture overview

_to fill — high-level: Kodi add-on (Python) + Windows configurator (Tauri 2 + React/TS) +
how the two pieces relate (configurator drives the add-on's existing
`resources/lib/installer.py` over SSH/SMB)._

# §6 Module map — add-on (Python)

_to fill — `default.py` / `service.py` entry points; `resources/lib/` modules
(oppo_control, avr_*, transfer file generation, installer, etc.)._

# §7 Module map — configurator (Tauri/React)

_to fill — `src-tauri/` Rust shell + `src/` React tree (shell/, screens/, state.ts,
steps.ts)._

# §8 Data model

_to fill — WizardState shape; add-on settings keys; `playercorefactory.xml` +
keymap schemas._

# §9 Key flow — Kodi handoff

_to fill — what happens when Kodi launches a UHD ISO; how the add-on routes to OPPO; the
TV input switch._

# §10 Key flow — configurator session

_to fill — 6-step wizard (Step 0 prereq → 1 Kodi box → 2 TV → 3 Player → 3.5 Inputs →
Test) and the state persistence boundary._

# §11 OPPO / clone control protocol

_to fill — port 23 IP control; `#PON` vs `#EJT` (clone wake-rewrite); `#QPW` query._

# §12 TV control backends

_to fill — adb / roku_ecp / sony_bravia / smartthings / lg_command / samsung_command /
custom_command; the basic-control-test gate; the ADB-weak input-finding fallback funnel._

# §13 Packaging boundaries

_to fill — `tools/package_installable_zip.py` allowlist (only addon.xml + default.py +
service.py + resources/ ship); how `configurator/` stays excluded; release evidence in
`release-evidence/`._

---

# §14 Gotchas (accumulate as hit)

_Format: `### YYYY-MM-DD — short title` · what bit us · how we recovered · how to prevent._

### 2026-05-29 — `build\_tmp` from the Windows pytest TEMP workaround can leave OS-locked dirs that break `audit_release.py`

- **What bit us:** an earlier session had used the historical Windows workaround
  (`$env:TEMP = build\_tmp; $env:TMP = $env:TEMP`) before running pytest. A handful of
  `build\_tmp\tmpXXXXXXXX\` subdirs ended up with ACLs that denied `Remove-Item`, `cmd
  rmdir /s/q`, `takeown /f`, and `icacls /grant` even from a normal user shell — likely
  Defender / a file-indexer holding handles. `tools/audit_release.py` walks the repo and
  prints `Can't list 'C:\…\build\_tmp\tmpXXX'` to stdout when it hits one; that line
  precedes the JSON payload and breaks two tests that call the audit CLI with `--json`:
  `tests/test_v291_build10_audit_reporter_refactor.py::test_audit_cli_json_output_still_works`
  and `tests/test_all.py::TBuild5ReleaseAuditArtifacts::test_release_audit_cli_json`.
- **How we recovered:** since the lock could not be cleared without admin/reboot,
  `Move-Item build\_tmp $env:USERPROFILE\build_tmp_LOCKED_delete_after_reboot` (rename
  only needs parent write access, not contents access) moved it out of the repo; the two
  tests then passed. Locked tree can be deleted with `rmdir /s/q` after the next reboot
  frees the handles.
- **How to prevent:** the full suite passed this session in ~8.5s **without** the
  `$env:TEMP=build\_tmp` override (just `--basetemp="build\_pt"` and
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`). The override may no longer be necessary on this
  machine. Try without it first; only reach for it if `WinError 5` (or a similar
  permission-denied) actually appears, and prefer routing TEMP to a path **outside the
  repo** (e.g. a freshly created `$env:USERPROFILE\.pytest-tmp`) so the audit walker
  cannot reach it.

---

# §15 Development journey

_Append-only, newest-last. One bullet per material commit or session-shaping decision._

- **2026-05-28** — Scaffolded the Windows configurator under `installer/` (Tauri 2 + Vite +
  React + TS, Direction A "Warm Paper" tokens). PR #30 opened as draft.
- **2026-05-28** — Renamed `installer/` → `configurator/` plus all identifiers (npm
  package, Cargo crate, Tauri bundle id) because the app *configures* an already-installed
  add-on; "installer" was a misnomer carried from the design handoff.
- **2026-05-28** — Ported all 21 remaining wizard screens from
  `docs/installuidraft/design_handoff_oppo_installer/prototype/` into typed TSX
  (`screens/step1.tsx` through `screens/test.tsx`). Bundle: 47 modules / 215 KB JS / 25 KB
  CSS.
- **2026-05-28** — Bootstrapped this AI handoff + agent norms structure
  (`CLAUDE.md`, `AGENTS.md`, `AI_RESUME_HANDOFF.md`, `docs/MANUAL_VERIFICATION_CHECKLIST.md`)
  per operator's job_finder_ri norms. Existing spine docs replaced wholesale. Issue model
  set to hybrid (Issues for bug/enhancement tracking, PRs for delivery).
- **2026-05-29** — ENH-#43: split the flat `resources/lib` (46 modules) into
  `tv/` / `oppo/` / `avr/` / `kodi/` sub-packages, canonical name
  `resources.lib.<bucket>.<module>`. A lazy `sys.meta_path` alias finder in
  `resources/lib/__init__.py` preserves legacy flat names (`resources.lib.X`
  and bare `X`) as same-object aliases during a deprecation window; `version.py`
  → `kodi/`. Draft PR #47. Established convention: module-top cross-family
  imports explicit (`from ..oppo… import`), lazy in-function imports bare
  (finder-resolved, mock-friendly).
- **2026-05-29** — Merged the two in-flight addon PRs onto `main`: **ENH-#43**
  lib split (PR #47 at `3ba5009`) and **ENH-#41 Parts B+C** configurator-owner
  hint (PR #46 at `f21033b`). The PRs overlapped on `service.py` /
  `tests/test_all.py` / the manual checklist despite the prior §3a "disjoint"
  note; integrated #46 onto the post-#47 `main` locally, ran the full gate on the
  combined tree (commit `126bac9`: 886/3, coverage 99.07%), then merged. `main`
  `23d43ae` → `f21033b`; test count 865 → 886.
- **2026-05-29** — ENH-#42 shipped (both halves): in-add-on network/IP editor (PR #48 at `16eda5e`) and add-on-language switcher (PR #49 at `3765862`). `installer.main()` gained "Network settings" + "Add-on language" entries; hidden `addon_language` setting; `i18n.supported_languages()` 7 → 12 plus `effective_language()` and a pinned-locale `L()` override.
- **2026-05-29** — ENH-#38 resolved: ruff enforced across the whole codebase (PR #50 at `092444a`). `ruff check .` + `ruff format --check .` clean (tests/ + tools/ included); config consolidated (ruff.toml authoritative + pyproject mirror, `C4` added); CI flipped to whole-tree. Filed ENH-#51 to track the mypy `--strict` source rollout (curated allowlist, leaf-first, source-only).
- **2026-05-29** — Configurator icon + bundling session (`area:configurator`). Generated the configurator's real app icon set from the repo-root add-on `icon.png` (256×256) via `tauri icon`, fixing a latent build-breaker (three `bundle.icon` files were missing on disk); pruned the mobile `ios/`/`android/` outputs and refreshed the icons README. First-pass `npm run tauri -- build` succeeded → MSI (3.0 MB) + NSIS setup (1.9 MB). Draft PR #52 (`claude/configurator-icon-bundle-h4n7k2p9`, tip `8cecd42`); `main` unchanged (configurator code lives under the PR). Software-verified only (build + bundle); installed-app/icon appearance not verified.
- **2026-05-29** — ENH-#51 mypy `--strict` rollout PR 1 (`area:addon`). Stood up an
  incremental strict gate instead of a global flip (source baseline **788 errors / 35
  modules** at py3.9): `mypy.ini` (authoritative) + `pyproject` mirror gain `strict`,
  `follow_imports = silent`, `python_version` 3.10 → 3.9, and a curated `files=`
  allowlist; `tools/type_check.py` gains a blocking `--gate` mode (default stays
  non-blocking) wired into a new CI `types` job. First 7-module leaf batch annotated to
  zero strict errors (signatures + stale-`# type: ignore` removal; no logic changes);
  `nas_playback_adapter` deferred (cascades into settings_reader/oppo_control). Guard
  tests (build-13, g6) updated in lockstep. Draft PR #53
  (`claude/enh51-mypy-strict-a7k3m2x9`, tip `62d811f`), all 9 CI checks green; `main`
  unchanged (work on the unmerged PR). Added memory `mypy-strict-gate-rollout`.
- **2026-05-29** — ENH-#51 mypy `--strict`: **merged PR 1** (PR #53) to `main` at
  `aa0cf68` (verified the combination — main's only advance since the PR base was
  docs-only; post-merge gate 933/3, coverage 99.10%, ruff + `mypy --gate` clean;
  branch purged) and **opened PR 2** (draft PR #54, `claude/enh51-mypy-pr2-k3n8m2q6`,
  tip `08a1b79`). PR 2 expands the gate `files=` allowlist **7 → 23**: 12 already-
  strict-clean modules locked in with zero code change (found via a full-tree
  landscape run) + 4 leaf modules annotated to zero strict errors (`arch_benchmark`,
  `diagnostic_logging`, `i18n`, `tv_control` — signatures + pinned locals, no logic
  changes). All CI green on #54. Established the **already-clean-lock-in** technique
  (memory `mypy-strict-gate-rollout` updated); next leaf groups are the `avr_*`
  type-fix backends, then a strategy for the `no-redef` import-fallback modules.
- **2026-05-29** — ENH-#51 PR 3 + **bulk-merge-all-pending**. (1) Shipped **PR 3**
  (the `avr_*` type-fix backends): annotated `avr_denon_marantz`/`avr_onkyo_eiscp`
  (socket `cast` to the `SocketLike` Protocol), `avr_yamaha`/`avr_sony_audio` (pin
  `urlopen().read()`; `cast` object-typed `int`/`list`/`map`/`meta.get` values),
  `avr_diagnostics` (`dict→dict` `@overload` on `sanitize_payload`; 2 stale ignores
  removed) → gate allowlist **23 → 28**, 34 strict errors cleared. Fixed a **latent
  Python 3.9 import bug**: `bytes | str` in the `HttpGet`/`SonyPost` module-level
  aliases is PEP-604 evaluated eagerly at import (not lazied by the `__future__`
  import) → `TypeError` on the 3.9 floor; → `typing.Union`. (2) On the operator's
  `merge all pending` directive, merged the whole open-PR queue to `main` in
  dependency order: **#54** (mypy PR 2) `56b7a17` → **#56** (mypy PR 3, recreated
  from auto-closed #55) `aa4143f` → **#52** (configurator icon) `859238e`. **Lesson:
  merging a PR with `--delete-branch` auto-CLOSES any PR stacked on that branch**
  (GitHub closes rather than retargets; a closed-with-deleted-base PR can't be
  reopened) — recreate it against `main`. `main` `aa0cf68` → `859238e`; post-merge
  gate **28/0**, `pytest -n auto` **933/3**, coverage **99%**. Memory
  `mypy-strict-gate-rollout` updated (PR 3 idioms + the stacking/verified-SHA
  lessons). All addon deliveries now merged; PR 4 = the `no-redef` import-fallback
  strategy (needs a design decision first).
- **2026-05-29** — ENH-#57 + README credits session (`area:addon`). Added a
  **change-scoped fast local test loop**: `tools/dev_test.py` wraps `pytest --testmon`
  so a local run executes only the tests affected by changed code (the full suite + 99%
  coverage gate stay the CI/`verify.sh`/pre-push backstop). Merged 4 PRs to `main`:
  [#59](https://github.com/skull-01/script.oppo203.iso.external/pull/59) `9f102a3`
  (the tool + `pytest-testmon` dev dep + `.testmondata` ignore + 5 guard tests; filed
  ENH-#57 to track it),
  [#58](https://github.com/skull-01/script.oppo203.iso.external/pull/58) `61999e3`
  (README **Credits** section),
  [#60](https://github.com/skull-01/script.oppo203.iso.external/pull/60) `343aff2`
  (Phase C checklist entry), and
  [#61](https://github.com/skull-01/script.oppo203.iso.external/pull/61) `2fdf869`.
  **CI lesson:** #59 reddened the **Python 3.9 compat-smoke** — `pytest-testmon` 2.2+
  dropped py3.9 but the add-on floor is 3.9, so `pip install -r requirements-dev.txt`
  failed there; repaired forward with an env marker (#61,
  `; python_version >= "3.10"`) and re-confirmed all six CI jobs green. Also found
  `tools/dev_build.py` is **not** on `main` (corrected the stale `dev-build-iteration-loop`
  memory) and that the `pre-push` hook runs the 99% coverage gate. `main` `859238e` →
  `2fdf869`; tests **933 → 938 passed, 3 skipped**, coverage **99.07%**, gate **28/0**.
- **2026-05-30** — ENH-#51 mypy `--strict` **PRs 4–7** (`area:addon`), completing the
  idiom + cascade scope the operator requested on `resume` ("do all of these" → "everything
  now"). Gate **28 → 46 modules** across four **stacked** draft PRs (merge #63→#64→#65→#66):
  **PR 4** [#63](https://github.com/skull-01/script.oppo203.iso.external/pull/63) `7568f89`
  (import-fallback leaf modules; settled the `no-redef` strategy = `# type: ignore[no-redef]`
  on the except-branch bare import only; `_FsLike` Protocol; `# type: ignore[attr-defined]`
  for hub re-exports); **PR 5** [#64](https://github.com/skull-01/script.oppo203.iso.external/pull/64)
  `8b06744` (the `settings_reader`+`oppo_control` hubs; `Settings.get`/`__getitem__` → `Any`;
  `HARDWARE_COMPAT` annotated to stop `object` inference); **PR 6**
  [#65](https://github.com/skull-01/script.oppo203.iso.external/pull/65) `8406b43` (the 7-module
  cascade group; nas_playback_adapter needed zero code change once the hubs were typed); **PR 7**
  [#66](https://github.com/skull-01/script.oppo203.iso.external/pull/66) `6fed436`
  (oppo_remote/external_player/installer/preset_manager). Annotations/casts/`# type: ignore`
  only — no behavior change; each verified `mypy --gate` 0 / `pytest -n auto` 938/3 /
  coverage ~99.05% / ruff clean. PRs 6–7's mechanical per-module annotation was **delegated to
  parallel general-purpose sub-agents** (one file each; `mypy --no-incremental` to avoid
  concurrent-cache corruption; cross-sibling no-untyped-call left for the combined gate), then
  verified on the main thread (gate + full suite + coverage + diff review). SHAs commented on
  #51; Phase-A entries per PR in the manual checklist. `main` unchanged (`c48bb43`) — all work
  on the unmerged PR branches. Memory `mypy-strict-gate-rollout` updated.

- **2026-05-30 (PM)** — ENH-#51 mypy `--strict` **rollout completed + full stack merged**
  (`area:addon`). On `resume` the operator picked ENH-#51 PR 8 and chose to base it on #66;
  built PR 8 ([#69](https://github.com/skull-01/script.oppo203.iso.external/pull/69) `fae98cb`)
  gating the last ungated source — `service.py` / `default.py` / `playercorefactory_merge`
  (gate 46→49, annotations/casts/`# type: ignore` only). Then on the operator's "merge
  everything", merged the whole stack to `main` in order: #63 `77305ee` → #64 `8dca608` →
  #65 `b636d30` → #66 `3f4d5cb` → #69 `4525d86` — **each child retargeted to `main` before its
  parent's branch was deleted**, avoiding the stacked-PR auto-close that bit #55. Post-merge
  `main` (`4525d86`) re-verified green: `mypy --gate` **49/0**, `pytest -n auto` 938/3, serial
  coverage 99.05%. Merge SHAs commented on #51 (stays open per the only-operator-closes norm).
  **ENH-#51 source rollout COMPLETE — every `resources/lib` module + top-level
  `service.py`/`default.py` is gated.** PR #68 (configurator wizard-state mapping) was left
  **open** — out of scope of the ENH-#51 merge, needs an in-area configurator session.
  **Tool-channel instability** recurred hard this session (Read / Grep / Bash+PowerShell stdout
  intermittently returned stale or fabricated content); mitigated by file-redirect readbacks,
  cross-channel checks, byte-validated Edits, and never reusing a pre-commit SHA. Memory
  `mypy-strict-gate-rollout` updated.
- **2026-05-30 (EOD — configurator review → fix → merge → close-out)** — Operator: `resume`
  → merged the two pending EOD docs (#70/#71, resolving a §3b add/add conflict by keeping #71's
  detailed §3b and folding in #70's `384d180` note) → `/code-review` of the wizard-wiring
  **PR #68** (filed 16 bugs **#72–#87**, `type:bug`/`area:configurator`) → "create a plan to
  close them all" → executed a 3-phase plan. **Phase 2:** fixed the 12 high/med bugs on the #68
  branch (commits `6d68206` Rust hardening / `7120439` config-write safety / `46d4ca8` IP-test +
  state) and **merged #68** (`454e5ab`). **Phase 3:** cleanup **PR #88** (`a4ad7ad`) —
  #85/#77/#86/#87 + ENH-#41 Part C (commits `d48b0c7`/`9acb6a1`/`384e3d4`; new `src/xml.ts` +
  `src/players.ts`). **Phase 4:** **PR #89** (`9401fb3`) — ENH-#44 hardware-validation
  solicitation (`docs/HARDWARE_VALIDATION.md` + README). All 18 issues SHA-commented + Phase-C
  checklist entries; none closed (operator's call). Configurator: 63 vitest + tsc/vite/cargo
  green; add-on 938/3, coverage 99.05%, mypy gate 49/0 unchanged. Recreated a wiped `.venv`
  mid-session (pre-push hook needs it). `main` `4525d86` → `9401fb3`. Key gotcha logged:
  PowerShell 5.1 splits native args containing `"` and mojibakes non-ASCII in inline scripts —
  use `--body-file` / Edit/Write for issue/PR/doc content, keep inline scripts ASCII.
- **2026-05-30 (evening — merge the PM-session PR stack + publish the first configurator
  binary)** — Operator: `resume` → picked **"merge all 6 green drafts."** Reviewed and merged
  the six PRs the 2026-05-30 PM session had left open as drafts (all base `main`, none stacked,
  all CI-green 8/8): **#93** `BUILD_PLAN.md` refresh (`6d657ea`), **#91** Chinoppo `M9205 V1`
  split (`36f9cbd`, `area:addon` — the only runtime code), **#94** configurator build recipe
  (`60f7897`), **#95** first-binary evidence (`4af93b5`), **#92** canonical Plan-format norm
  (`dce80cd`), and **#96** this handoff. `main` `0f9fd67` → `dce80cd` (+ the #96 merge).
  **Published `configurator-v0.1.0`** — flipped the PM session's draft GitHub release to a
  public **pre-release** (tag at `dce80cd`; MSI 3.15 MB + NSIS 2.05 MB + SHA-256 sidecars;
  unsigned, software-verified only; the add-on's v2.9.13 stays repo "Latest"). Re-verified the
  **combined** `main` green before publishing/finalizing: add-on `ruff` clean, `mypy --gate`
  **49/0**, `sync_version` 2.9.13, `pytest -n auto` **943/3**, serial coverage **99%**;
  configurator `tsc -b` + `vite build` clean, **vitest 64/64**; `main`@`dce80cd` CI green.
  Order discipline: confirmed **#94 ⊂ #95** (`merge-base --is-ancestor`) so #94→#95 merged
  clean; **#92 and #96 both touch this file**, so #96 was merged **last** and its branch was
  **reset to `main` + re-authored** to the merged reality (its original "5 open drafts, none
  merged" content was made false by this very session). **Both §3a and §3b rewritten** (session
  touched both areas); **§17a** #51→CLOSED + new #91 / v0.1.0-binary rows + "Last refreshed"
  bumped; **§19** updated. The agent closed no issues (operator closed #51); the M9205 split and
  the binary are PR-only themes (no SHA-comment target).
- **2026-05-30 (EOD — backlog clear + done-for-the-day)** — After the merge/release work above,
  the operator reviewed the open backlog and directed **"close all of these; I will create a new
  list after testing."** Closed the 21 delivered issues (addon #38/#41/#42/#43/#57 + configurator
  #72–#87) ahead of on-device verification — each with a note that they'll re-file what's still
  outstanding after hardware testing — and kept **#44** (the standing hardware-validation call)
  open. This explicitly waived the standing "only the operator closes issues" norm, confirmed via
  a popup before the agent ran `gh issue close`. Net backlog: **1 open issue (#44), 0 open PRs.**
  Then this done-for-the-day doc refresh: header "Last sync" `dce80cd` → `6fc8615`, §3a/§3b
  reflect the cleared backlog, §17a flipped the closed rows + "Last refreshed" bumped. No code
  changed; `main` stays green (943/3, 99%, mypy 49/0). Pushed via a doc-only PR.
- **2026-05-30 (post-EOD — code-commentary theme scoped + Step-1 map; PAUSED)** — After the
  backlog-clear EOD, the operator pivoted to a new theme: **teaching-grade code commentary for a
  near-beginner reviewer** (comments + docstrings only; no behavior/format/reorder change; teach
  the real end-to-end flow; running suspect list — see §3c). Ran **Step 1** only: mapped the repo
  + the actual playback flow (two architectures converging on `external_player.py`; fan-out
  sub-agents mapped OPPO control / Kodi routing / TV+AVR) and recommended `external_player.py` as
  the first file. Operator then said **"hold it"** — **no code or comments were written.** The
  exact plan (mandate + 3-step process + flow map + batch plan + estimate + preliminary suspect
  list) is saved in **§3c** and now leads the §3a/§3b resume themes. `main` unchanged (943/3,
  coverage 99%, mypy 49/0).
- **2026-05-30 (evening — configurator `v0.2.0` integration + release; `area:configurator`)** —
  Integrated an operator-uploaded design-revision changeset (a zip laid out at real repo paths)
  onto a branch, ran the configurator gate, and shipped it as the **second** Windows release.
  **PR #99** (`32ae49c`): the wizard rename (files/ids/components/labels → displayed step
  numbers — Player 2 / TV 3 / HDMI Input 4, `step35.tsx`→`step4.tsx`, `steps.ts` as source of
  truth) + the design-review pass (reordered stepper/chain, animated chain icons, Step 0 prep
  table, Tier A SSH note) + real `simple-icons` brand badges (new `BrandIcon.tsx`;
  `simple-icons@^16.21.0` dep; `siTcl`/`siHisense`/`siVizio` dropped from the import since the
  package no longer carries them → device-glyph fallback) + the AGENTS.md "names match the UI"
  norm. **PR #100** (`6fa8c76`): version bump `0.1.0 → 0.2.0` (3 guarded pins + lockfiles) +
  `release-evidence/v0.2.0/BUILD_NOTES.md`. Built MSI (3,162,112 B) + NSIS (2,059,233 B) via
  `npm run dist`, tagged `configurator-v0.2.0` at `1b31941`, published as a full GitHub release
  marked **Latest** (moving the repo-wide badge off add-on `v2.9.13`, per the operator's
  choice). Software-verified only (cargo built clean; `tsc` + 64 vitest green); not run live /
  no hardware validation. One cosmetic follow-up noted: Sony's white mark on the white badge
  renders invisible (`styles.css:769`), left as-authored.
- **2026-05-30 (later — teaching-commentary Step 2)** — Addon session under the cross-area
  teaching-commentary theme (§3c). Commented `resources/lib/kodi/external_player.py` to the teaching
  bar — module docstring + numbered end-to-end playback-flow overview, import-shim explanation,
  beginner docstrings on every previously-undocumented function in the pipeline, and one trick-play
  gloss. **Comments/docstrings only — no logic, renames, reindents, or reordering** (+171 lines, 1
  file). Backstop: `ruff check` + `ruff format --check` clean; full suite **943 passed / 3 skipped**.
  Checkpointed as `wip:` `62b22eb` on `claude/teaching-comments-extplayer-r3k8m2x9` (pushed, **not**
  on `main`, **not** merged) — awaiting the operator's Step-2 style sign-off before continuing to
  `oppo_control.py`. Flagged one latent bug found while reading (not fixed): `hold_playback`'s
  `verbose_push` fallback degrades to `fixed_timeout` instead of `tcp_qpl_poll`. `main` unchanged.
- **2026-05-30 (later still — TV DB schema v2 + players DB; configurator `v0.3.0`)** — Configurator
  session, two enhancements merged then released. **[#103](https://github.com/skull-01/script.oppo203.iso.external/issues/103) / [PR #104](https://github.com/skull-01/script.oppo203.iso.external/pull/104)** `5380425`: TV DB migrated to **schema
  v2** — `tvdb.ts` tier `preferred|fallback|probe`, `primary_backend`/`fallback_backends`/`regions`/
  `platform`/`mapping_confidence`, gate `schema_version === 2`, `modelsForRegion`; both
  `tv-models.json` copies replaced with the **296-row 2018–2025** payload; Step 3 region-first
  filtering + the new fields surfaced. **[#105](https://github.com/skull-01/script.oppo203.iso.external/issues/105) / [PR #106](https://github.com/skull-01/script.oppo203.iso.external/pull/106)** `81c3eb5`: canonical
  `players.json` (configurator/src + docs, byte-identical) consolidating the 18-model OPPO/clone
  taxonomy + candidate regions; `playersdb.ts` + `players.ts` derive `PLAYER_BRANDS` from it; Step 2
  surfaces markets/wake/class/NAS; **add-on test-only** drift guard
  (`tests/test_players_db_consistency.py`) + the two `==18` counts now derive from the DB. Then
  **release [PR #107](https://github.com/skull-01/script.oppo203.iso.external/pull/107)** `55bf6fa`: bump `0.2.0→0.3.0` + evidence; published **`configurator-v0.3.0`**
  (MSI + NSIS attached, unsigned). Gates green: configurator `tsc` / **74 vitest** / build; add-on
  pytest **950/3**, ruff, mypy `--gate` **52/0**, coverage **99%**, audit **580/580**; browser-preview
  pass of Step 2 + Step 3. **Deliberately NOT done (install-base safety):** no `settings.xml` enum
  regeneration, no `hardware_presets.py` change, no add-on release (no runtime change). All rows
  `validated:false`.

---

# §16 Open questions (strategic decisions blocking work)

(none open)

_Add as: `### YYYY-MM-DD — title` · context · the decision needed · who decides._

---

# §17 Backlog audit — narrative

_Current state of every open issue, with one-line context per issue. Maintained by the
operator + on-demand via the `backlog audit` trigger. Empty until first issues filed under
the hybrid model._

(none)

---

# §17a Backlog audit cache

_Refreshable snapshot queried by the `backlog audit` trigger. Agents read from here first
before re-scanning live GitHub state (operator norm #10). The `Area` column is the
`area:addon` / `area:configurator` label that drives the per-area split in §1._

Last refreshed: **2026-06-03 (EOD #21 — Addon v2.9.16 + configurator v0.9.5 both shipped).** This session filed **1 new issue** — **#334** (ENH, area:configurator — installer single old-version prompt via a vendored NSIS template) — **implemented + merged to `main` (PRs #335/#336/#337) + SHA-commented + left OPEN** (only-operator-closes; shipped in configurator v0.9.5). No issues closed/retitled (the 18 folded `area:addon` issues #221–#224/#226–#233/#235–#237/#254/#256/#275 were SHA-commented as "shipped in v2.9.16" but remain **OPEN**). Backlog now **47 open** (46 prior + #334) — almost entirely the confirmation queue. **Open PRs: 0.** _Prior:_ **2026-06-03 (EOD #19 — quality + capability roll-up; cut configurator v0.9.4 via the CI tag).** This session filed **2 new issues** — **#329** (`type:bug`, area:addon — `int()` port/option coercion crashes in `discovery` + `autoscript_helper`, found by the property-test pass) and **#331** (ENH, area:configurator — AVR raw-command console) — both **implemented + merged to `main` + SHA-commented + left OPEN** (only-operator-closes; #329 via PR #330, #331 via PR #332; both ride configurator v0.9.4). The dev-console **hardening** (PR #328) merged with **no issue** (adversarial-review fixes). No issues closed/retitled. Backlog now **46 open** (44 prior + #329 + #331) — almost entirely the confirmation queue. **Open PRs: 0.** _Prior:_ **2026-06-03 (EOD #14 — v0.8.5/v0.8.6/v0.8.7 + first configurator CI + Developer Options plan locked).** This session filed **2 new `type:bug` issues** — **#266** (configurator — Reset-all hangs on an unreachable device) and **#275** (addon — `http_info_indicates_playing` `OverflowError` on a non-finite numeric status) — both **implemented + merged to `main` + SHA-commented + left OPEN** (only-operator-closes; #266 shipped in v0.8.5, #275's fix in v0.8.6). No issues closed/retitled. Backlog now **44 open — almost entirely the confirmation queue** (implemented + shipped, awaiting operator verify+close): **33 `type:bug`** (the 2026-06-02 audit #221–#256 + #266 + #275) + **11 ENH** (Pure-HTTP #207–#217, dashboard #167/#168, DB #103/#105); the one genuinely-open non-code item is **#44** (addon tester solicitation). The **Developer Options console** plan is **LOCKED + queued** (§3b ▶ NEXT THEME; the OPPO HTTP catalog #285 already landed). **Open PRs: 0.** _Prior:_ **2026-06-03 (EOD #13 — #263 Reset-all reachability shipped; cut configurator v0.8.4).** This session implemented **#263** (configurator, `type:bug`) — Reset all configurations now reachable from a persistent app-header entry + the Step 0 gate — merged via PRs **#264/#265** and shipped in **configurator-v0.8.4** (holds "Latest"; bundles add-on v2.9.15); **#263 SHA-commented + left OPEN** (only-operator-closes; Phase-C pending). No other issues opened/closed/retitled. **Open PRs: 0.** _Prior:_ **2026-06-03 (EOD #12 — full-audit remediation + 4 configurator features/releases).** This session filed **~27 new `type:bug` issues (#221–#256, `area:addon` + `area:configurator`)** for the 2026-06-02 full audit (4 High + 10 Medium + 16 Low; H2 + L12 included after the operator approved them) — **all implemented + merged to `main` + SHA-commented + left OPEN** (only-operator-closes; Phase-C pending) across PRs **#225/#234/#238/#245/#253/#255/#257**. Three further configurator changes merged with **no issue** (data/feature; operator files ENHs): TV-DB +110 rows (PR #258), reset-all (PR #260), installer old-version check (PR #262). **Three configurator releases** cut — **configurator-v0.8.1 / v0.8.2 / v0.8.3** (v0.8.3 holds "Latest"). Prior-open issues unchanged: **#44** (addon tester solicitation), **#103/#105/#167/#168** (configurator, implemented/shipped), **#207/#209/#211/#213/#215/#217** (Pure-HTTP ENHs, open for close); **#263** (configurator — Reset-all button effectively unreachable, `type:bug`, filed post-EOD + queued as the next configurator theme). **Open PRs: 0.** _Prior:_ **2026-06-02 (EOD #11 — Xnoppo V3 / Pure-HTTP shipped).** This session opened **6 new `area:` ENH issues**, all **implemented + merged to `main` + SHA-commented + left OPEN** (only-operator-closes; Phase-C pending): **#207** (PR1 HTTP/436 primitives · addon), **#209** (PR2 7th preset + http monitor · addon), **#211** (PR3 pure-HTTP orchestration · addon), **#213** (PR6 checkfolderhasBDMV · addon), **#215** (PR4 default flip + process-monitor transport · configurator), **#217** (PR5 HDMI switching · addon). Prior-open issues are unchanged: **#44** (addon — tester solicitation) + **#103/#105/#167/#168** (configurator — implemented/shipped, ready to close). **Open PRs: 0.** _Prior:_ **2026-06-02 (EOD #10 — merged the cfg queue + shipped add-on `v2.9.14` & configurator `v0.7.0`; queued the Pure-HTTP build).** Issue state was unchanged from EOD #8 — **5 open**: **#44** (addon — hardware-tester solicitation), **#103/#105/#167/#168** (configurator — **all now implemented + shipped**: #103/#105 already on `main`, #167/#168 delivered via #201/#202 in configurator v0.7.0; their stale PRs **#165/#166 were closed** this session; all ready for operator close). **Open PRs: 0.** _Prior:_ **2026-06-02 (EOD #8 — Phases 3/4/5 merged + verification queue cleared).** Per the
operator's "close all items that need my manual verification so nothing is blocked, but keep the checklist"
directive, this session **closed 23 confirmation-queue issues** — this session's ENH #176/#178/#180/#182/#191–#197
(+ #199 for the TV-backend-persist follow-up), and the already-merged prior addon backlog #111–#117/#123,
#150–#152, #113, #173 — all software-verified + merged to `main`, with the on-device steps RETAINED in
`docs/MANUAL_VERIFICATION_CHECKLIST.md`. **Now 5 open:** **#44** (addon — hardware-tester solicitation umbrella),
**#103/#105** (configurator — DB backlog, not implemented), **#167/#168** (configurator dashboard ENH — their
PRs **#165/#166** are unmerged + now **CONFLICTING** against the rebuilt dashboard). **Open PRs: 0.**
_(The per-issue table below predates this sweep and is not individually re-stated — `gh issue list` is authoritative.
Prior EOD #5: ENH #167/#168 filed. EOD #4: dashboard D1/D2/D3 + wire-transcripts #153 merged.)_

| # | Title | Area | Labels | State | Implementing SHA(s) | Operator-verified? |
|---|---|---|---|---|---|---|
| 22 | [Bug]: wizard launch failure (`No module named 'wizard'`) | addon | `bug`, `area:addon` | CLOSED 2026-05-28 | `b7471db` on `wip/wizard-ux` (wizard now removed entirely by `3abf486` on `claude/strip-wizard-g4feovqi`, merged via #40 at `59eb511`) | closed by operator |
| 38 | ENH-: clear ruff backlog on main (336 errors, 172 auto-fixable, 66% in 3 test files) | addon | `area:addon` | CLOSED 2026-05-30 | **Resolved** by [PR #50](https://github.com/skull-01/script.oppo203.iso.external/pull/50) at `092444a` — `ruff check .` + `ruff format --check .` clean whole-codebase, enforced in CI | closed by operator 2026-05-30 (pre-hardware-test) |
| 41 | ENH-: configurator owns add-on configuration; add-on is read-mostly | addon | `area:addon` | CLOSED 2026-05-30 | Part A `816bde2` (PR #45). Addon side of Parts B + C **merged** via [PR #46](https://github.com/skull-01/script.oppo203.iso.external/pull/46) at `f21033b`. **Configurator side of Part C done** via PR #88 (`d48b0c7`) — provenance marker written into the generated settings.xml. | closed by operator 2026-05-30 (pre-hardware-test; Phase A/C still queued) |
| 42 | ENH-: minimal in-add-on settings menu (TV/OPPO/AVR/Kodi IPs + language) | addon | `area:addon` | CLOSED 2026-05-30 | **Merged** via [PR #48](https://github.com/skull-01/script.oppo203.iso.external/pull/48) at `16eda5e` (network/IP editor) + [PR #49](https://github.com/skull-01/script.oppo203.iso.external/pull/49) at `3765862` (language switcher) | closed by operator 2026-05-30 (pre-hardware-test; Phase A/C still queued) |
| 43 | ENH-: split `resources/lib` into TV / Oppo / AVR / Kodi sub-packages | addon | `area:addon` | CLOSED 2026-05-30 | **Merged** via [PR #47](https://github.com/skull-01/script.oppo203.iso.external/pull/47) at `3ba5009` (impl `18a97a6` + test-isolation `69e32b3`) | closed by operator 2026-05-30 (pre-hardware-test; Phase A still queued) |
| 44 | ENH-: hardware-validation testing — lending, donations, tester reports wanted | addon | `area:addon` | OPEN | **Solicitation merged** via [PR #89](https://github.com/skull-01/script.oppo203.iso.external/pull/89) at `9401fb3` — `docs/HARDWARE_VALIDATION.md` (per-family status matrix + how to help) + README pointer | awaiting operator (standing community call) |
| 51 | ENH-: roll out mypy --strict across add-on source (curated allowlist, leaf-first) | addon | `area:addon` | CLOSED 2026-05-30 | **ROLLOUT COMPLETE — all merged to `main` 2026-05-30 PM (gate→49).** PRs 1–3 (`aa0cf68`/`56b7a17`/`aa4143f`, →28), then PRs 4–8 merged in order: #63 `77305ee` (→33), #64 `8dca608` (→35), #65 `b636d30` (→42), #66 `3f4d5cb` (→46), #69 `4525d86` (service.py/default.py/playercorefactory_merge →49). Post-merge `main` green: gate 49/0, pytest 938/3, coverage 99.05%. | **closed by operator 2026-05-30** |
| 68 | configurator: wire the wizard to the add-on contract (slices 1–7) | configurator | _untracked theme (PR-only)_ | MERGED 2026-05-30 | [PR #68](https://github.com/skull-01/script.oppo203.iso.external/pull/68) at `454e5ab` — 7-slice wizard wiring; a /code-review filed 16 bugs (#72–#87), the 12 high/med fixed on-branch before merge (`6d68206`/`7120439`/`46d4ca8`) | software-verified; Phase C on-device queued |
| 52 | (no issue) configurator app icon + first MSI/NSIS bundle | configurator | _untracked theme_ | MERGED 2026-05-29 | [PR #52](https://github.com/skull-01/script.oppo203.iso.external/pull/52) at `859238e` — real icon set replaces the PR #35 stub; fixes a latent `bundle.icon` build-breaker; MSI 3.0 MB + NSIS 1.9 MB | Phase C on-device (install, confirm icon + launch) queued |
| 57 | ENH-: change-scoped fast local test loop (pytest-testmon) | addon | `area:addon` | CLOSED 2026-05-30 | **Merged** via [PR #59](https://github.com/skull-01/script.oppo203.iso.external/pull/59) at `9f102a3` (`tools/dev_test.py` + `pytest-testmon` dev dep + 5 guard tests); py3.9-marker fix [PR #61](https://github.com/skull-01/script.oppo203.iso.external/pull/61) `2fdf869` | closed by operator 2026-05-30 (pre-hardware-test; Phase C software check queued) |
| 72–87 | configurator PR #68 review bugs (config-write safety, ssh/probe/deploy hardening, IP-control test, persisted state, + cleanups) | configurator | `type:bug`, `area:configurator` | CLOSED 2026-05-30 (16 issues) | Fixed across [PR #68](https://github.com/skull-01/script.oppo203.iso.external/pull/68) `454e5ab` (12 high/med — `6d68206`/`7120439`/`46d4ca8`) + [PR #88](https://github.com/skull-01/script.oppo203.iso.external/pull/88) `a4ad7ad` (5 cleanups + ENH-#41 Part C). SHA commented on each. | closed by operator 2026-05-30 (pre-hardware-test; Phase C on-device queued) |
| 91 | (no issue) Chinoppo M9205 V1 split into a distinct hardware model | addon | _untracked theme (PR-only)_ | MERGED 2026-05-30 | [PR #91](https://github.com/skull-01/script.oppo203.iso.external/pull/91) at `36f9cbd` — new `chinoppo_m9205_v1` enum **appended** to settings.xml, mirrored through settings_reader/hardware_profiles/hardware_capabilities as an exact M9205 clone; configurator `players.ts` re-pointed; +5 tests, count guards 17→18 | software-verified; Phase A/C on-device queued |
| 94–95 | (no issue) configurator first Windows binary v0.1.0 (build recipe + evidence) | configurator | _untracked theme (PR-only)_ | MERGED + PUBLISHED 2026-05-30 | [PR #94](https://github.com/skull-01/script.oppo203.iso.external/pull/94) `60f7897` (build recipe: `BUILD.md`, `dist` alias, version guard) + [PR #95](https://github.com/skull-01/script.oppo203.iso.external/pull/95) `4af93b5` (evidence + notes); release **`configurator-v0.1.0`** published as a public pre-release (MSI + NSIS, unsigned) | Phase C on-device (install on clean machine, confirm launch) queued |
| 99–100 | (no issue) configurator `v0.2.0` — wizard rename + design pass + release | configurator | _untracked theme (PR-only)_ | MERGED + PUBLISHED 2026-05-30 | [PR #99](https://github.com/skull-01/script.oppo203.iso.external/pull/99) `32ae49c` (rename to displayed step numbers + design-review pass + `simple-icons` brand badges + AGENTS.md norm) + [PR #100](https://github.com/skull-01/script.oppo203.iso.external/pull/100) `6fa8c76` (bump 0.1.0→0.2.0 + build evidence); release **`configurator-v0.2.0`** published full/**Latest** (MSI + NSIS + SHA-256, unsigned) | Phase C on-device (install on clean machine, confirm launch + renamed wizard order Player 2 → TV 3 → HDMI 4) queued |
| 92–93 | (no issue) canonical Plan-format norm + BUILD_PLAN.md refresh | meta | _untracked theme (PR-only, docs)_ | MERGED 2026-05-30 | [PR #92](https://github.com/skull-01/script.oppo203.iso.external/pull/92) `dce80cd` (Plan-format norm in AGENTS.md + §1/§4 triggers + CLAUDE.md pointer) + [PR #93](https://github.com/skull-01/script.oppo203.iso.external/pull/93) `6d657ea` (BUILD_PLAN.md refresh) | docs-only; no verification needed |
| 103 | ENH: migrate configurator TV database to schema v2 (296 model families, region filtering) | configurator | `area:configurator` | OPEN (SHA commented) | [PR #104](https://github.com/skull-01/script.oppo203.iso.external/pull/104) `5380425` (impl `343041c` loader+data, `cde87c6` Step-3 UI). Shipped in `configurator-v0.3.0`. | awaiting operator verify/close (Phase C in checklist) |
| 105 | ENH: create canonical players DB (players.json) and adopt it in the configurator | configurator | `area:configurator` | OPEN (SHA commented) | [PR #106](https://github.com/skull-01/script.oppo203.iso.external/pull/106) `81c3eb5` (impl `4b7f63e` DB, `9ab2f61` configurator, `18d423e` guard, `5675f70` count derive). Add-on side test-only. Shipped in `configurator-v0.3.0`. | awaiting operator verify/close (Phase C in checklist) |
| 104·106·107 | (no issue) configurator `v0.3.0` — TV DB v2 + players DB + release | configurator | _release (PR-only)_ | MERGED + PUBLISHED 2026-05-30 | release [PR #107](https://github.com/skull-01/script.oppo203.iso.external/pull/107) `55bf6fa`; tag `configurator-v0.3.0` (MSI 3,166,208 B + NSIS 2,065,049 B + SHA-256 attached, marked **Latest**); evidence `configurator/release-evidence/v0.3.0/BUILD_NOTES.md` | Phase C on-device (install on clean machine; confirm Step 3 region filter + Step 2 player facts) queued |
| 111 | [Bug] addon: diagnostics HTTP probe checks port 80 but the OPPO HTTP API is port 436 | addon | `type:bug`, `area:addon` | OPEN — **merged to `main`** | [PR #132](https://github.com/skull-01/script.oppo203.iso.external/pull/132) merge `bd0cc42` — `run_diagnostics_dashboard` gains `http_port=436`; `_http` probes it, not 80 | awaiting operator (Phase C / close) |
| 112 | [Bug] addon: verbose_push hold silently degrades to fixed_timeout (180 min) instead of tcp_qpl_poll | addon | `type:bug`, `area:addon` | OPEN — **merged to `main`** | [PR #129](https://github.com/skull-01/script.oppo203.iso.external/pull/129) merge `396634c` — verbose_push `except` now calls `_hold_tcp_qpl_poll` (no fall-through to the blind sleep) | awaiting operator (Phase C / close) |
| 113 | ENH-: verify the OPPO actually started playing the requested file (both architectures) | addon | `area:addon` | OPEN (SHA-commented) | precursor probe shipped — [PR #118](https://github.com/skull-01/script.oppo203.iso.external/pull/118) `c9f7579`; **`#QFN`** is the documented basis (protocol finding commented). `verify_playback_started()` is the follow-up. | awaiting operator (run probe Phase C, then build verify) |
| 114 | [Bug] addon: default hold_mode=fixed_timeout holds Kodi for 180 min with no stop detection | addon | `type:bug`, `area:addon` | OPEN — **merged to `main`** | [PR #130](https://github.com/skull-01/script.oppo203.iso.external/pull/130) merge `523eadc` — default → `tcp_qpl_poll` (reader + settings.xml index); merged after #129 | awaiting operator (Phase C / close) |
| 115 | [Bug] addon: manual_file hold mode has no timeout (infinite hang) | addon | `type:bug`, `area:addon` | OPEN — **merged to `main`** | [PR #129](https://github.com/skull-01/script.oppo203.iso.external/pull/129) merge `396634c` — `manual_file` bounded by the `fixed_timeout` ceiling | awaiting operator (Phase C / close) |
| 116 | [Bug] addon: http_poll/tcp_qpl_poll hold to the 240-min timeout when the OPPO drops off mid-playback | addon | `type:bug`, `area:addon` | OPEN — **merged to `main`** | [PR #129](https://github.com/skull-01/script.oppo203.iso.external/pull/129) merge `396634c` — end the hold after `MAX_CONSECUTIVE_POLL_FAILURES`=5 unreachable polls | awaiting operator (Phase C / close) |
| 117 | [Bug] addon: stale oppo203iso-active sentinel after a crash disables interception / sticks the remote bridge | addon | `type:bug`, `area:addon` | OPEN — **merged to `main`** | [PR #131](https://github.com/skull-01/script.oppo203.iso.external/pull/131) merge `29d951f` — shared `session_is_active()` staleness (6h mtime); both readers delegate | awaiting operator (Phase C / close) |
| 118 | (no issue) read-only OPPO player-status probe (#Q.. query battery + protocol reference) | addon | _PR-only_ | **MERGED 2026-05-31** | [PR #118](https://github.com/skull-01/script.oppo203.iso.external/pull/118) merge `8c35f28` (docs-only checklist conflict resolved on merge); precursor for #113. Gates: pytest 963/3, cov 99%, ruff+mypy clean | Phase C queued (run probe on real hardware → unblocks #113) |
| 119 | (no issue) addon functional-flow diagrams doc (Mermaid) | addon | _PR-only (docs)_ | **MERGED 2026-05-31** | [PR #119](https://github.com/skull-01/script.oppo203.iso.external/pull/119) merge `1a22c06` | docs-only; no verification needed |
| 120·122·124·125·127·128 | (no issue) configurator: Sony badge, Sony AVR auto-enable, naming-consistency sweep | configurator | _PR-only_ | **MERGED 2026-05-31** | #120 Sony badge dark-chip; #122 Sony AVR auto-enable (PSK+ack+URI); #124 `oppoInput`→`playerInput`; #125 `players.json`→`players-models.json`; #127 handoff map; #128 `docs/NAMING_CONVENTIONS.md` + historical flags. 103 vitest + build green. (#121 v0.5.0 checklist entry + artifact SHA verify merged too.) | Phase C (clean-machine install + Sony hardware) queued |
| 123 | [Bug] addon: ruff format --check is red on main (3 unformatted test files) | addon | `type:bug`, `area:addon` | OPEN — **merged to `main`** | [PR #133](https://github.com/skull-01/script.oppo203.iso.external/pull/133) merge `43207ba` — `ruff format` the **2** actually-drifted files (`test_all.py`, `test_players_db_consistency.py`); the named 3rd was already clean. `ruff format --check .` on `main` now green | awaiting operator (close) |
| 126 | (no issue) rename TV backend modules to `tv_` prefix (parity with `avr_`) | addon | _PR-only_ | **MERGED 2026-05-31** | [PR #126](https://github.com/skull-01/script.oppo203.iso.external/pull/126) — `adb_control`/`roku_ecp_control`/`smartthings_control` → `tv_*`; alias-finder/`mypy.ini`/`pyproject.toml`/`lib_buckets.py`/imports/6 tests updated; module bodies unchanged. Gate green (963/99%). | software-only; no hardware impact |
| 134·135 | (no issue) configurator AVR follow-ups — DB consistency vitest + Step-5 reachability probe | configurator | _PR-only_ | **MERGED 2026-05-31** | [PR #134](https://github.com/skull-01/script.oppo203.iso.external/pull/134) `fbe98d2` (`avr_db_consistency.test.ts` pins the two `avr-models.json` copies + schema invariants) + [PR #135](https://github.com/skull-01/script.oppo203.iso.external/pull/135) `721c3ed` (Step-5 **Test reachability** button reusing the generic `tv_port_probe`; Denon 23 / Yamaha 80 / Onkyo·Pioneer 60128; Sony+custom none). 111→123 vitest + build green. | Phase C on-hardware (real receiver reachability) queued |
| 136·137·138 | (no issue) configurator two playback chains — topology picker + flow/viz + mapping | configurator | _PR-only_ | **MERGED 2026-05-31** | [PR #136](https://github.com/skull-01/script.oppo203.iso.external/pull/136) `1e8f678` (Step-0 picker + `state.topology`) + [PR #137](https://github.com/skull-01/script.oppo203.iso.external/pull/137) `51a2a0a` (Receiver chain node + Step-4 receiver wording + pure helpers in `topology.test.ts`) + [PR #138](https://github.com/skull-01/script.oppo203.iso.external/pull/138) `2ae4b16` (mapping emits `avr_power_on_enabled`/`avr_restore_*`, gates `tv_switching_enabled` off in the AVR chain). Soft default; no add-on change. build + 123 vitest green. | Phase C on-hardware (AVR-chain switch test) queued |
| 167 | ENH: dashboard settings-snapshot diff (Configuration changes card) | configurator | `area:configurator` | OPEN (SHA commented) | draft [PR #165](https://github.com/skull-01/script.oppo203.iso.external/pull/165) `9b15e93` — reads + sanitizes + diffs the box's `settings.xml` (masks `sony_psk`/`smartthings_token`/`sony_avr_psk`); new Rust `read_app_json`/`write_app_json`. Software-verified (tsc 0 / 194 vitest / build / cargo 8). | awaiting operator verify/close (Phase C in checklist) |
| 168 | ENH: dashboard historical session log (Session history card) | configurator | `area:configurator` | OPEN (SHA commented) | draft [PR #166](https://github.com/skull-01/script.oppo203.iso.external/pull/166) `1408eab` (stacked on #165) — pure `foldObservation` persists a deduped, capped-50 session history reusing #165's appdata store. Software-verified. | awaiting operator verify/close (Phase C in checklist) |

---

# §18 Reserved

_(intentionally empty — preserved for future use)_

---

# §19 Updates to this document

_Meta-log of changes to this handoff itself. Dated, newest-last. Maintained by
`done for the day`._

- **2026-05-28** — Bootstrapped from scratch per operator's job_finder_ri norms. Replaced
  the prior 397-line PR-only handoff. Sections §1 / §2 / §2a / §3 / §4 filled; §5–§17a /
  §19–§21 seeded as headers.
- **2026-05-28 (EOD)** — First `done for the day` cycle. Refreshed §3 to point at PR #30
  awaiting review + the chain of follow-up themes; both branches confirmed pushed and in
  sync with origin (`main`@`636ae35`, `claude/windows-installer-ui-gfv4m`@`edba3d1`). No
  issues opened/closed/retitled — §17a cache remains empty.
- **2026-05-29 (EOD)** — Verification + cleanup session, no code changes. Refreshed §3
  to record today's work (claude-review CI fix verified to the limit of what can be
  proven before the next dependabot batch; memory hygiene); added the first §14 Gotcha
  (`build\_tmp` Windows-locked tmpdirs vs. `audit_release.py`); updated the header
  "Last sync" / "Tests on `main`" to `4e54c5d` / 987 passed, 3 skipped. PR #30 unchanged.
  §17a still empty (no issues opened/closed/retitled).
- **2026-05-29 (spine-revision branch — EODs #2, #3)** — Parallel history on
  `docs/eod-handoff-2026-05-29-pm` (PR #37). Authored the §3a/§3b two-area
  restructure of §1, §2a, §3, AGENTS.md, `.claude/commands/resume.md`,
  `docs/ai-handoff/AI_RESUME_GUIDE.md` §9; ran one addon session under the new
  spine (audited `wip/wizard-ux` for v2.9.14, fixed a single ruff I001 in
  `tools/dev_build.py`, filed issue #38 for the 336-error ruff backlog).
  **Header "Last sync" on that branch was `394f9fc`** (the PR #30 merge); tests
  on `wip/wizard-ux` were 999 passed / 3 skipped / 99.10% coverage. The §3a/§3b
  content authored on that branch is preserved only via this entry — the actual
  §3a/§3b on `main` was overwritten by the PM bulk-merge entry below.
- **2026-05-29 (EOD — strip-wizard session)** — End-of-day after a single-theme
  addon session that stripped the in-Kodi setup wizard from the add-on. PR
  [#40](https://github.com/skull-01/script.oppo203.iso.external/pull/40) on
  `claude/strip-wizard-g4feovqi` (tip `92a9408`) was open as draft. 44 files
  changed, +313 / −5814. Tests: **865 passed, 3 skipped** in ~10s on the strip
  branch; coverage **99.05%** (≥ 99% floor). Filed 4 new `area:addon` ENH
  issues — #41 configurator-owns-config policy, #42 in-add-on settings menu,
  #43 module split (TV/Oppo/AVR/Kodi), #44 hardware-testing solicitation.
  Created [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) on `main` (commit
  `3967cb6`) with the strategic direction + open-issue grid + suggested
  ordering. Header "Last sync" updated from `4e54c5d` to `3967cb6`; tests on
  `main` re-confirmed at **987 passed, 3 skipped** in ~12s. §3 rewritten to
  record the strip-wizard PR + new issues; §17a backlog cache populated for
  the first time (with Area column added) — six rows: #22 (closed), #38, #41,
  #42, #43, #44.
- **2026-05-29 (EOD — config-owner-policy session)** — Second `done for
  the day` cycle on 2026-05-29, after the strip-wizard EOD at `7b65ed2`.
  Single-theme addon session that drafted **Part A** (policy doc) of
  [ENH-#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41).
  PR [#45](https://github.com/skull-01/script.oppo203.iso.external/pull/45) on
  `claude/config-owner-policy-a3k7m2nq` (tip `1ed15a3`) opened as draft.
  3 files changed, +70 / −1: [`AGENTS.md`](AGENTS.md) gained
  `## Configuration is owned by the configurator`,
  [`CONTRIBUTING.md`](CONTRIBUTING.md) gained `## Configuration ownership`
  (matching policy framed for external contributors),
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md)
  gained a Phase A row for the #45 review. Tests on the policy-doc branch:
  **987 passed, 3 skipped** in 10.69s; coverage **99.08%**. SHA `1ed15a3`
  commented on issue #41 per the only-operator-closes-issues norm. Parts B + C
  of #41 deferred to the next session — both touch `resources/settings.xml`,
  which PR #40 also modifies.
- **2026-05-29 (PM — bulk-merge session)** — Operator typed `resume` then
  directed "merge all pending, operator will skip review." Bulk-merged the
  five mergeable PRs in dependency order:
  [#40](https://github.com/skull-01/script.oppo203.iso.external/pull/40)
  strip-wizard at `59eb511`,
  [#45](https://github.com/skull-01/script.oppo203.iso.external/pull/45)
  config-owner-policy Part A at `816bde2` (after resolving a
  `docs/MANUAL_VERIFICATION_CHECKLIST.md` conflict that preserved both #40 and
  #45 Phase A entries),
  [#33](https://github.com/skull-01/script.oppo203.iso.external/pull/33)
  window-control IPC at `45c6572`,
  [#34](https://github.com/skull-01/script.oppo203.iso.external/pull/34) state
  persistence at `bc60074`,
  [#35](https://github.com/skull-01/script.oppo203.iso.external/pull/35) cargo
  unblock at `12e5b18`. Closed three superseded/stale PRs without merge:
  [#39](https://github.com/skull-01/script.oppo203.iso.external/pull/39)
  (wip/wizard-ux — predecessor of #40),
  [#36](https://github.com/skull-01/script.oppo203.iso.external/pull/36) (stale
  mid-day handoff),
  [#32](https://github.com/skull-01/script.oppo203.iso.external/pull/32) (stale
  §3 refresh + ruff-target line now in tension with #38). Resolved this PR
  ([#37](https://github.com/skull-01/script.oppo203.iso.external/pull/37) the
  two-area spine revision) against the new `main`: took #37's structural
  changes (§1 step 2 multi-area wording, §2a's 14-row table with `auto-repo` /
  `auto-system` / `manual` tiers, §3a/§3b split, AGENTS.md area-label rule,
  `.claude/commands/resume.md` two-area procedure, AI_RESUME_GUIDE.md §9
  update); took `main`'s §17a (6 rows); rewrote §3b to record the four
  configurator-area PR outcomes this session; **§3a still carries the stale
  wip/wizard-ux v2.9.14 content from #37 and will be overwritten by the next
  EOD**. `pytest -n auto --basetemp=build\_pt` on `main` after the five
  merges: **865 passed, 3 skipped in 10.40s** (test count dropped from 987 →
  865 because #40 deleted the wizard test files; coverage **99.05%** ≥ 99%
  floor). Phase A on-device verification of #40 was **NOT** performed —
  operator chose to defer per the skip-review directive; revert remains
  available if hardware testing later flags an issue. No `area:configurator`
  labels back-applied to any prior items in this session.
- **2026-05-29 (EOD — `done for the day` after PM bulk-merge)** — Doc-only
  refresh. Header "Last sync" updated from `7b65ed2` to `bc79649` (PR #37
  merge); test count updated from 987 → **865 passed, 3 skipped** to reflect
  the wizard test files deleted by #40 (coverage **99.05%** on the lower
  denominator). **§3a rewritten** to drop #37's stale wip/wizard-ux v2.9.14
  content (replaced by main's current addon state: PR #40 + #45 shipped, #41
  Parts B + C unblocked, five open addon issues #38/#41/#42/#43/#44, candidate
  themes refreshed). **§3b dedeuplicated** (two "As of" headers merged into
  one, no content change beyond noting the `configurator-icon-files-missing`
  memory was pruned this EOD and adding a fourth candidate theme for the
  configurator-side ENH-#41 Part C). **§2a parenthetical** updated to note PR
  #35 satisfied row 13 (icon stub). **Memory pruned:** deleted
  `configurator-icon-files-missing.md` (carved out by PR #35); MEMORY.md index
  updated. **No new code commits, no new issues, no new branches.** Tree
  clean; `pytest -n auto --basetemp=build\_pt` on `main` re-confirmed at 865
  passed / 3 skipped / 9.95s.
- **2026-05-29 (EOD — ENH-#41 Parts B + C addon session)** — Single-theme
  addon session that implemented the addon-side of
  [ENH-#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41)
  Parts B (in-add-on guidance hint) and C (configurator-managed-key
  overwrite warning). PR
  [#46](https://github.com/skull-01/script.oppo203.iso.external/pull/46) on
  `claude/enh41-bc-config-hint-a4n9k2m` (tip `3ccd9f1`) opened as draft. 17
  files changed, +697 / -3:
  [`service.py`](service.py) gained the `CONFIGURATOR_MANAGED_KEYS`
  constant (42 keys), `_snapshot_managed_settings` /
  `_changed_managed_keys` / `_resolve_localized` /
  `_notify_config_hint_once_per_session` /
  `_warn_overwritten_managed_keys` helpers, and a new `Monitor.__init__`
  + `Monitor.onSettingsChanged` that fires Part B's once-per-session
  toast and Part C's per-key warning (the class docstring records the
  no-state-mutation invariant preserved from PR #40);
  [`resources/settings.xml`](resources/settings.xml) gained one `<setting
  id="config_owner_hint" label="30290" type="lsep"/>` at the top of
  `<category id="connection">` (`tests/test_all.py` settings-count
  assertion bumped 97 → 98); 12 PO files gained four new strings (#30290
  banner, #30291 notification body, #30292 per-key warning template with
  `{key}` placeholder, #30293 notification title — non-en_gb files use
  msgid=msgstr fallback per convention);
  [`tests/test_v2914_build1_config_owner_hint.py`](tests/test_v2914_build1_config_owner_hint.py)
  is new with 21 tests across 5 classes (`TManagedKeysContent`,
  `TSnapshotAndDiff`, `TNotificationHelpers`, `TMonitor`,
  `TSettingsXmlAndPo`);
  [`docs/MANUAL_VERIFICATION_CHECKLIST.md`](docs/MANUAL_VERIFICATION_CHECKLIST.md)
  gained a Phase A entry with a six-step Phase C on-device verification
  script for #46. Tests on the work branch: **886 passed, 3 skipped** in
  ~9.5s (the +21 over `main`'s 865 are this PR's new tests); ruff clean
  on touched Python files (257 pre-existing repo-wide errors covered by
  [ENH-#38](https://github.com/skull-01/script.oppo203.iso.external/issues/38)).
  SHA `3ccd9f1` commented on issue #41 per the only-operator-closes
  norm. Kodi-API caveat documented in the PR body: there is no "settings
  dialog opened" event; Part B's "first-open" notification is
  implemented as "first **change** per session", with the always-visible
  lsep banner as the on-open counterpart. **§3a rewritten** to record
  open draft PR #46, what's done, what's left, and refreshed candidate
  themes. **§3b not touched** (no configurator work this session).
  **§17a row for #41 updated** to record the Parts B + C SHA on draft
  PR #46 (configurator side of Part C still pending). **Header
  unchanged** — "Last sync" stays at `bc79649` and tests-on-`main` at
  865/3/99.05% because `main` had no operational changes this session.
  Phase A on-device verification of #46 deferred to next session; Phase
  A of #40 still deferred from PM bulk-merge.
- **2026-05-29 (EOD — ENH-#43 lib sub-package split session)** — Two-part
  addon session. (1) **Drove PR #46 to green:** the ENH-#41 B+C PR's "Lint and
  format checks" CI job was failing on a `ruff format` diff in `service.py`'s
  `CONFIGURATOR_MANAGED_KEYS` tuple (the PR's local gate had run `ruff check`
  but not `ruff format --check`); committed `52f1cd7` to fix it — all 7 PR
  checks now green and mergeable. (2) **Implemented ENH-#43** on draft
  [PR #47](https://github.com/skull-01/script.oppo203.iso.external/pull/47)
  (`claude/enh43-lib-subpackages-r9k2m4x7`, tip `69e32b3`): moved all 46
  `resources/lib` modules into `tv/`/`oppo/`/`avr/`/`kodi/` (incl. `version.py`
  → `kodi/`); added a lazy `sys.meta_path` alias finder in
  `resources/lib/__init__.py` so legacy flat names (`resources.lib.X` + bare
  `X`) resolve to the same canonical objects; made module-top cross-family
  imports explicit while keeping lazy in-function imports bare; updated the
  `version.py` importers in `sync_version.py` (project-root sentinel),
  `package.yml`, `package_release.sh`, `verify.sh`, `audit_release.py`; updated
  ~70 flat-path test literals + the kodi-stub contexts (new
  `tests/_support/lib_buckets.py`) + new `tests/__init__.py` for the
  unittest-discover path; pragma'd 12 now-dead bare-name fallback branches;
  added a per-test isolation fixture (`69e32b3`) to remove `-n auto` flakiness
  the move exposed. Gates: `pytest -n auto` 865/3 (green across repeats),
  serial coverage **99.07%**, ruff check+format clean, `unittest discover`
  484 OK, `audit_release` 580/580, runtime ZIP 70 files (50 bucketed). SHA
  `18a97a6` commented on issue #43. **§3a rewritten** to record both in-flight
  PRs (#46 + #47); **§3b untouched** (no configurator work). **§15** gained an
  ENH-#43 journey bullet; **§17a** #43 row + #41 tip + "Last refreshed"
  updated. **Header unchanged** — `main` had no operational changes this
  session (ENH-#43 lives on the branch / PR #47, not merged). Software-verified
  only; Phase A + Phase C steps for #47 queued in the manual checklist.
- **2026-05-29 (EOD — PR #47 + #46 merge session)** — Addon session that drove
  the two in-flight draft PRs to merge. Reviewed both; found the prior §3a
  "disjoint files" claim was wrong (they overlap on `service.py` /
  `tests/test_all.py` / `docs/MANUAL_VERIFICATION_CHECKLIST.md`). Merged **PR #47**
  (ENH-#43 lib split) at `3ba5009`; then integrated the new `main` into **PR #46**'s
  branch locally (clean auto-merge), ran the **full gate on the combined tree**
  (commit `126bac9`: `pytest -n auto` 886/3, serial coverage 99.07%, ruff clean,
  `unittest discover` 505 OK, `audit_release` 580/580, doc/version/i18n/layout
  `--check` OK), pushed (pre-push hook re-ran the coverage gate), waited for CI
  green, then merged **PR #46** (ENH-#41 Parts B+C) at `f21033b`. Both
  `claude/enh4*` branches deleted. Merge SHAs commented on issues #43 and #41
  (left open for operator). **§3a rewritten** to the merged state + a "verify the
  combination, not two green CIs" lesson; **§3b untouched** (no configurator
  work). **§15** gained a merge bullet; **§17a** rows #41/#43 + "Last refreshed"
  updated. **Header** "Last sync" `bc79649` → `f21033b`, tests `865` → **886
  passed, 3 skipped**, coverage `99.05%` → **99.07%**. No new issues/branches;
  ENH-#42 now unblocked by #43's bucket layout. Phase A/C on-device verification
  of #40/#46/#47 still deferred.
- **2026-05-29 (EOD — ENH-#42 + ruff-enforcement session)** — Operator-driven session. (1) Landed the finished ENH-#42 PRs to `main`: #48 network/IP editor at `16eda5e`, #49 language switcher at `3765862` (retargeted #49 to `main` before deleting #48's branch to avoid stacked-PR auto-close). (2) ENH-#38 ruff backlog **resolved** via PR #50 at `092444a` — `ruff check .` + `ruff format --check .` clean across tests/tools, consolidated config (ruff.toml authoritative + pyproject mirror + `C4`), CI flipped to whole-tree; 246 findings cleared, no source touched. Filed **ENH-#51** to track the mypy `--strict` rollout (source-only, curated allowlist, leaf-first) — Phase 2, not started. **§3a rewritten** to the merged state + the in-flight #51 plan; **§3b untouched**. **§15** gained two journey bullets; **§17a** rows #38/#42 + new #51 row + "Last refreshed" updated. **Header** "Last sync" `f21033b` → `092444a`, tests `886` → **932 passed, 3 skipped**, coverage `99.07%` → **99.10%**.
- **2026-05-29 (EOD — configurator icon + bundling session)** — Single-theme `area:configurator` session (`resume` → operator picked "icon + bundling"). Generated the real app icon set from the add-on artwork via `npm run tauri -- icon ..\icon.png` (replacing the PR #35 stub), pruned the `ios/`/`android/` outputs, refreshed `src-tauri/icons/README.md`, and produced the first Windows installers via `npm run tauri -- build` (MSI 3.0 MB + NSIS 1.9 MB, exit 0, ~1m13s). Two commits on `claude/configurator-icon-bundle-h4n7k2p9`: `eb9f1cf` (icon set) + `8cecd42` (Phase A/C checklist entry); draft **PR #52** opened. **§3b rewritten** to the in-flight #52 state + refreshed candidate themes (purpose-built icon now leads); **§3a untouched** (no addon work). **§15** gained a journey bullet. **§17a untouched** — no issues opened/closed/retitled (this theme has no tracked issue). **Header unchanged** — `main` had no operational changes (configurator code lives under unmerged PR #52); tests on `main` stay 932/3/99.10%. Added memory `configurator-tauri-build-recipe`. Suite re-confirmed green this session: 932 passed, 3 skipped.
- **2026-05-29 (EOD — ENH-#51 mypy --strict PR 1 session)** — Single-theme `area:addon` session (`resume` → operator picked ENH-#51). Shipped **PR 1** of the mypy `--strict` rollout to draft [PR #53](https://github.com/skull-01/script.oppo203.iso.external/pull/53) (`62d811f`): an incremental strict gate (`files=` allowlist + `follow_imports = silent` + `tools/type_check.py --gate` + new CI `types` job), `python_version` 3.10 → 3.9, the now-unused `[mypy-tests.*]` override dropped, and the first 7-module leaf batch annotated to zero strict errors (no logic changes; `nas_playback_adapter` deferred — cascades into settings_reader/oppo_control). Guard tests **build-13** (config shape) and **g6** (CI `types` job + gate command) updated in lockstep; SHA `62d811f` commented on #51; Phase A entry added to `docs/MANUAL_VERIFICATION_CHECKLIST.md`. **§3a rewritten** to the in-flight PR #53 state + refreshed candidate themes (PR 2 leads); **§3b untouched** (no configurator work). **§15** gained a journey bullet; **§17a** #51 row + "Last refreshed" updated. **Header unchanged** — `main` had no operational changes (ENH-#51 lives on unmerged PR #53); tests on `main` stay 932/3/99.10%. Added memory `mypy-strict-gate-rollout`. All 9 PR #53 CI checks green; software-verified only, hardware validation not claimed.
- **2026-05-29 (EOD — ENH-#51 mypy --strict PR 1 merge + PR 2 session)** — `resume` → operator picked addon, then drove the ENH-#51 rollout across two PRs (within §4's 4-PR cap). (1) **Merged PR 1**: drove draft [PR #53](https://github.com/skull-01/script.oppo203.iso.external/pull/53) to `main` at `aa0cf68` — verified the combination first (main's only advance since the PR base was docs-only), marked ready, merged with `--delete-branch`, post-merge gate green (933/3, coverage 99.10%, ruff + `mypy --gate` clean), and fixed a dangling checklist `Implementing SHA` ref to the merged commit (`3e79ec6` on `main`). (2) **Opened PR 2**: draft [PR #54](https://github.com/skull-01/script.oppo203.iso.external/pull/54) (`claude/enh51-mypy-pr2-k3n8m2q6`, tip `08a1b79`, impl `92f2373`) expanding the gate `files=` allowlist **7 → 23** — 12 already-strict-clean modules locked in with zero code change (found via a full-tree landscape run) + 4 leaf modules annotated to zero strict errors (`arch_benchmark`, `diagnostic_logging`, `i18n`, `tv_control`; signatures + pinned locals, no logic changes). All CI green on #54 (Release + Type gate + compat 3.9/3.10/3.12 + lint + build ZIP + claude-review). **§3a rewritten** to the merged-PR-1 + in-flight-PR-2 state with PR-3 themes (the `avr_*` type-fix backends lead); **§3b untouched** (no configurator work). **§15** gained a journey bullet; **§17a** #51 row + "Last refreshed" updated. **Header** "Last sync" `092444a` → `aa0cf68`, tests `932` → **933 passed, 3 skipped** (coverage 99.10%). Memory `mypy-strict-gate-rollout` updated with the already-clean-lock-in technique. #51 stays open (multi-PR rollout); PR #54 awaiting operator review/merge.
- **2026-05-29 (EOD — ENH-#51 PR 3 + bulk-merge-all-pending session)** — `resume` → operator picked addon ENH-#51 PR 3, then said `merge all pending`. (1) **Shipped PR 3** (the `avr_*` type-fix backends): annotated the five remaining AVR backends to zero strict errors (allowlist 23 → 28, 34 errors cleared — socket `cast` to `SocketLike`, pinned `urlopen().read()`, `cast` object-typed `int`/`list`/`map`/`meta.get` values, a `dict→dict` `@overload` on `avr_diagnostics.sanitize_payload`, 2 stale `# type: ignore` removed) and fixed a **latent Python 3.9 import bug** (`bytes | str` module-level aliases evaluate eagerly at import → `TypeError` on 3.9; → `typing.Union`). (2) **Merged the whole open-PR queue** in dependency order: **#54** mypy PR 2 → `56b7a17`, **#56** mypy PR 3 (recreated from #55, which auto-closed when #54's base branch was deleted) → `aa4143f`, **#52** configurator icon → `859238e`; all branches purged. **Both §3a and §3b rewritten** to the merged state (this session touched both areas). **§15** gained a journey bullet (incl. the stacked-PR-auto-close lesson); **§17a** #41/#51 rows updated + new #52 row + "Last refreshed". **Header** "Last sync" `aa0cf68` → `859238e` (tests stay **933/3**, coverage 99%, gate **28/0**). Memory `mypy-strict-gate-rollout` updated (PR 3 idioms + stacking/verified-SHA process lessons). **Mid-session correction:** an issue-comment draft used a SHA predicted before committing (`ce97c69`); the content-integrity classifier correctly blocked it; re-posted with the real SHA `d36e76f` — nothing fabricated reached the repo or GitHub. All addon deliveries now merged; next is ENH-#51 PR 4 (the `no-redef` import-fallback strategy — needs a design decision first).
- **2026-05-29 (EOD — ENH-#57 fast-test-loop + README credits session)** — `resume` → operator picked an ENH-#43 follow-up, which they redefined as **change-scoped local testing** and (via the popup decision model) scoped to **pytest-testmon, local build loop only**. Built `tools/dev_test.py` (wraps `pytest --testmon` — only tests affected by changed code run) + `pytest-testmon` dev dep + `.testmondata` ignore + 5 guard tests; filed **ENH-#57** and merged it as [PR #59](https://github.com/skull-01/script.oppo203.iso.external/pull/59) `9f102a3`. Also merged the **README Credits** section ([PR #58](https://github.com/skull-01/script.oppo203.iso.external/pull/58) `61999e3`; Moremodey1 → AVForums per operator), a Phase C checklist entry ([PR #60](https://github.com/skull-01/script.oppo203.iso.external/pull/60) `343aff2`), and a **py3.9 fix** ([PR #61](https://github.com/skull-01/script.oppo203.iso.external/pull/61) `2fdf869`) after #59 reddened the 3.9 compat-smoke (testmon 2.2+ needs py≥3.10; gated the dev dep with a `; python_version >= "3.10"` marker). **§3a rewritten** to the merged state + the CI lesson; **§3b untouched** (no configurator work). **§15** gained a journey bullet; **§17a** new #57 row + "Last refreshed" updated. **Header** "Last sync" `859238e` → `2fdf869`, tests **933 → 938 passed, 3 skipped**, coverage **99.07%**, gate 28/0; full CI green on `main` (six jobs, verified). Memory `dev-build-iteration-loop` corrected (dev_build.py not on main; pre-push hook = coverage gate; dev-dep 3.9-marker rule). **Process note:** #59 was merged before CI finished, on local-3.12 evidence — the 3.9 matrix was the gap; **wait for CI green before merging dependency changes.** This EOD doc pushed via a doc-only PR (direct-to-`main` push is harness-blocked).
- **2026-05-30 (EOD — ENH-#51 mypy --strict PRs 4–7)** — `resume` → operator picked ENH-#51,
  said "do all of these" (the no-redef idiom modules + the cascade group), then chose
  **"everything now (PR 6+7)"** at the mid-session checkpoint. Shipped the whole idiom +
  cascade scope as **four stacked draft PRs** (gate **28 → 46 modules**): #63 (leaves) → #64
  (hubs) → #65 (cascade) → #66 (idiom modules); merge in that order. Annotations-only; each
  green locally (`mypy --gate` 0, `pytest -n auto` 938/3, coverage 99.04–99.05%, ruff clean).
  PRs 6–7 delegated to parallel sub-agents (`--no-incremental` to avoid mypy-cache races),
  verified by the combined gate + full suite + diff review. **§3a rewritten** to the 4-draft
  state + the merge-order resume steps + optional-PR-8 themes; **§3b untouched** (no
  configurator work). **§15** gained a journey bullet; **§17a** #51 row + "Last refreshed"
  updated. **Header** "Last sync" `2fdf869` → `c48bb43` (main carries the prior EOD PR #62;
  this session's ENH-#51 work is on the unmerged PRs, so main's gate stays **28/0** and tests
  **938/3**). Memory `mypy-strict-gate-rollout` updated (PRs 4–7 + the parallel-sub-agent
  technique). **§21** gained the scope-decision Q&A. This EOD doc pushed via a doc-only PR
  (direct-to-`main` push is harness-blocked).
- **2026-05-30 (PM EOD — ENH-#51 stack merge + done-for-the-day)** — Operator: "merge
  everything and done for the day." Merged the ENH-#51 stack #63→#64→#65→#66→#69 to `main`
  (tip `4525d86`), retargeting each child to `main` first to avoid the stacked-PR auto-close;
  left configurator PR #68 open (out of scope). Post-merge `main` re-verified (gate 49/0,
  938/3, coverage 99.05%); merge SHAs commented on #51. **Header** "Last sync" `c48bb43` →
  `4525d86`, gate **28 → 49**, coverage 99.07% → 99.05%. **§3a** rewritten to the
  completed-and-merged state; **§3b** gained a PM note (open PR #68 + the operator `384d180`
  upload of `configurator/CONFIGURATOR_HANDOFF.md` + installer zip); **§17a** #51 row →
  COMPLETE/merged, new #68 row, "Last refreshed" bumped; **§15** gained a merge-session bullet.
  This doc pushed via a doc-only PR (direct-to-`main` push is harness-blocked).
- **2026-05-30 (EOD — configurator review/fix/merge + done-for-the-day)** — After merging the
  two pending EOD docs (#70/#71), ran `/code-review` on PR #68 (filed #72–#87), then executed a
  3-phase close-out: fixed the 12 high/med bugs on the #68 branch and merged #68 (`454e5ab`);
  cleanup PR #88 (`a4ad7ad`, #85/#77/#86/#87 + ENH-#41 Part C); doc PR #89 (`9401fb3`, ENH-#44).
  **Header** "Last sync" `4525d86` → `9401fb3` + configurator-hardening summary + a 63-vitest
  line. **§3a** reframed to this configurator-led EOD (addon touches = #44 + #41 Part C; mypy
  still complete). **§3b** rewritten — #68 merged + hardened, #88 cleanup, no configurator work
  in flight, the 16 review bugs listed as open-awaiting-close. **§15** gained a
  review→fix→merge entry; **§17a** #68 → MERGED, new #72–#87 row, #41/#44 rows updated, "Last
  refreshed" bumped. All 18 issues SHA-commented (none closed — operator's call). Doc pushed via
  a doc-only PR (direct-to-`main` push is harness-blocked).
- **2026-05-30 (norm addition — canonical plan format)** — Operator: "every time I ask for
  a plan, follow this level of detail/quality/output", citing an example multi-PR plan from
  another repo. Distilled it (adapted to this repo's gates) into a new **`## Plan format`**
  section in [`AGENTS.md`](AGENTS.md) (ground-first → theme → per-PR scope blocks →
  dependency chain → 📊 rollup → ⚠️ risk callouts → verification regime → ✅/🛑/🔁), plus a
  §1 trigger row + a §4 build-norm bullet here and a `plan` / `scope this` entry in the
  `CLAUDE.md` trigger-vocabulary pointer. Docs-only; no code touched. Shipped via a doc-only
  PR (direct-to-`main` push is harness-blocked).
- **2026-05-30 (evening — merge the PM-session 6-PR stack + publish v0.1.0 + this handoff
  refresh)** — Operator: `resume` → **"merge all 6 green drafts."** Merged #93/#91/#94/#95/#92
  to `main` (`0f9fd67` → `dce80cd`), published `configurator-v0.1.0` as a public pre-release,
  and landed this doc as **#96**. To keep this file honest, **#96's branch was reset to `main`
  and re-authored** — its original PM-session content described #91–#95 as "open drafts," which
  this session merged. **Header** "Last sync" `9401fb3` → `dce80cd` + the merge/release summary,
  tests `938/3` → **943/3**, vitest `63` → **64**, ENH-#51 marked CLOSED. **§3a** rewritten
  (M9205 V1 split merged; #51 closed; long ENH-#51 history condensed — full detail stays in
  §15). **§3b** rewritten (v0.1.0 binary published; M9205 follow-up resolved). **§15** gained a
  merge/release journey bullet. **§17a** #51 → CLOSED, three new rows (#91, #94–95 binary,
  #92–93 docs), "Last refreshed" bumped. Combined `main` re-verified green (943/3, coverage 99%,
  mypy 49/0, ruff clean; configurator tsc/vite + vitest 64; `main`@`dce80cd` CI green). No new
  issues/branches; the agent closed nothing (operator closed #51). This doc pushed via PR #96
  (direct-to-`main` push is harness-blocked).
- **2026-05-30 (EOD — backlog clear + done-for-the-day doc refresh)** — After the evening
  merge/release session (entry above), the operator directed `done for the day`. No code work was
  uncommitted (the 6-PR stack + v0.1.0 were already on `main`). Earlier in the session the operator
  had closed the 21 delivered issues (#38/#41/#42/#43/#57 + #72–#87) ahead of hardware testing,
  keeping only #44. This refresh trues the doc to that: **header** "Last sync" `dce80cd` →
  `6fc8615` + a "backlog cleared" clause; **§3a/§3b** "carried open" / "open configurator issues"
  bullets rewritten to the cleared state (only #44 open); **§17a** flipped #38/#41/#42/#43/#57 +
  the #72–#87 row to CLOSED and bumped "Last refreshed"; **§15** gained a backlog-clear bullet. No
  code touched; `main` green (943/3, coverage 99%, mypy 49/0). Pushed via a doc-only PR
  (direct-to-`main` push is harness-blocked).
- **2026-05-30 (post-EOD — save the code-commentary plan)** — Operator pivoted to a teaching-
  commentary theme, ran Step-1 mapping, then paused ("hold it") before any edit. Per operator
  request ("save exact plan in the ai handoff and add it to the proposed themes during resume"),
  added **new §3c** (the exact plan: mandate + 3-step process + Step-1 flow map + batch plan +
  estimate + preliminary suspect list) and led both the §3a addon and §3b configurator
  candidate-theme lists with it (PAUSED / resume-here → §3c). **§15** gained a Step-1 journey
  bullet. **No code or comments written; no header / §17a change** — `main` unchanged (943/3,
  coverage 99%, mypy 49/0). This handoff edit is **saved to the working tree only**; commit/push
  pending operator direction.
- **2026-05-30 (post-EOD — verbatim resume briefing pinned)** — Follow-up operator directive:
  "show this exact verbatim during resume when you propose this theme." Embedded the canonical
  Step-1 briefing (repo map + real end-to-end flow + first-file pick + preliminary suspects +
  time estimate) **verbatim** in §3c as a fenced block with a "reproduce exactly, no paraphrase"
  directive; flagged the same on the §3a/§3b theme lines. Replaced §3c's earlier paraphrased
  Step-1 / batch / suspect subsections with the verbatim block so there is a single canonical
  source. Still saved to the working tree only; no code touched.
- **2026-05-30 (EOD — done for the day; commentary plan pushed)** — Operator: `done for the day`.
  **No code changed this session** (resume → held the earlier comment-strip plan → pivoted to the
  teaching-commentary theme → Step-1 repo/flow map via 3 parallel sub-agents + spine read → saved
  the plan). Committed + pushed the session's `AI_RESUME_HANDOFF.md` edits (the §3c plan + the
  verbatim resume briefing + the §3a/§3b theme flags + the §15 bullet) via a doc-only PR
  (direct-to-`main` push is harness-blocked) — this supersedes the two "saved to the working tree
  only" notes above. Re-ran the suite as the EOD green-check: **943 passed, 3 skipped** in ~13s
  (`pytest -n auto`); `main` otherwise unchanged (coverage 99%, mypy 49/0; §17a backlog unchanged —
  only #44 open). Header "Last sync" trailing clause updated to this doc. **No new feature work;
  the theme stays PAUSED at Step 2 (`external_player.py`).**
- **2026-05-30 (evening EOD — configurator `v0.2.0` shipped; `done for the day`)** —
  Single-theme `area:configurator` session: integrated an operator-uploaded design-revision
  changeset, merged it (**PR #99** `32ae49c`), bumped + cut the release (**PR #100** `6fa8c76`),
  and published **`configurator-v0.2.0`** (MSI + NSIS + SHA-256, full release marked **Latest**).
  All code was already merged to `main` server-side before this EOD, so nothing was uncommitted.
  This refresh: **header** "Last sync" `6fc8615` → `1b31941` + a v0.2.0 clause and the moved
  "Latest" badge; **header** "Latest release" now names both add-on `v2.9.13` and configurator
  `configurator-v0.2.0` (repo "Latest"); **§3b** overwritten to the clean v0.2.0 stopping point
  (+ the Sony white-on-white cosmetic follow-up); **§3a / §3c unchanged** (addon untouched;
  teaching-commentary theme still PAUSED at Step 2); **§15** gained a v0.2.0 journey bullet;
  **§17a** gained the #99/#100 delivery row (no issue state changed — only #44 open). Tests on
  `main`@`1b31941`: addon **943 passed, 3 skipped** (pre-push hook; coverage 99%, mypy 49/0);
  configurator **64 vitest + `tsc` green** (re-run this session). Pushed via a doc-only PR
  (direct-to-`main` push is harness-blocked). **No new feature work.** Also noted the untracked
  `.claude/launch.json` (a local dev-server launch config, pre-existing — not this session's
  work) left unstaged.
- **2026-05-30 (later EOD — teaching-commentary Step 2; `done for the day`)** — Single-theme
  `area:addon` session under the cross-area teaching-commentary theme (§3c). Commented
  `resources/lib/kodi/external_player.py` (comments/docstrings only, +171 lines); checkpointed as
  `wip:` `62b22eb` on branch `claude/teaching-comments-extplayer-r3k8m2x9` (**pushed**; the pre-push
  hook ran the suite — **943 passed / 3 skipped**). Per §3c the commentary is the operator's to
  review/push, so it was **NOT** merged to `main` — the wip branch is the off-machine backup,
  awaiting the operator's Step-2 style sign-off. This refresh: **header** "Last sync"
  `1b31941`→`d89f0ae` (Merge #101) + a teaching-Step-2 clause; **§3a** overwritten to the in-flight
  Step-2 checkpoint; **§3c** status moved "PAUSED before Step 2" → "Step 2 written — awaiting style
  sign-off" (verbatim briefing block untouched), incl. the `verbose_push`-fallback suspect; **§15**
  gained a Step-2 journey bullet; **§3b unchanged** (configurator untouched); **§17a unchanged** (no
  issue opened/closed/retitled — only #44 open). Doc pushed via a doc-only PR (direct-to-`main` push
  is harness-blocked). The untracked `.claude/launch.json` left unstaged. **No new feature work.**
- **2026-05-30 (EOD — TV DB v2 + players DB; configurator `v0.3.0` shipped)** — Configurator
  session (operator: "go on everything, complete fully automated … create a new release and push").
  Delivered + merged two enhancements and cut a release. Doc refresh: **header** "Last sync" → `55bf6fa`
  / configurator `v0.3.0` / tests `950/3` + mypy `52/0` + 74 vitest; **§3b** overwritten to the v0.3.0
  clean state (TV DB schema v2 #103/#104, players DB #105/#106, release #107), the "Resume here next"
  TV-DB-grow item marked done and the smoke-test item retargeted to v0.3.0; **§3a** gained a durable
  bullet for the test-only players-DB consistency guard (the teaching-commentary WIP block left
  **untouched** — still awaiting the operator's Step-2 sign-off); **§15** gained the
  TV-DB-v2/players-DB journey bullet; **§17a** added the #103, #105, and #104·106·107 release rows
  (refresh date bumped). New ENH #103/#105 opened + delivered this session, SHAs commented, awaiting
  operator close; Phase C rows added to `docs/MANUAL_VERIFICATION_CHECKLIST.md`. The untracked
  `.claude/launch.json` (preview-server config) left unstaged. **No new feature work.**
- **2026-05-30 (AVR database — configurator `v0.4.0`)** — operator dropped a fact-checked AVR
  model bundle and asked to "do the same for AVRs as the TV DB, then publish." Added
  `configurator/src/avr-db/avr-models.json` (+ canonical docs copy) — **224 AV-receiver/processor
  model families 2018–2025**, 10 brands, schema v2 (the TV-DB twin) — a typed `avrdb.ts` loader,
  an optional **Step 5 (AV Receiver)** picker, and 18 vitest cases. [PR #109](https://github.com/skull-01/script.oppo203.iso.external/pull/109) (merge `6251cdf`),
  tag/release `configurator-v0.4.0` (MSI 3,174,400 B / NSIS 2,069,995 B). Configurator-only — the
  DB isn't loaded by the add-on at runtime, so no add-on release. Updated the §1 header pointer.
- **2026-05-30 (AVR wiring — configurator `v0.5.0`)** — follow-up: on "continue" the operator
  chose to give Step 5 true TV/Player parity by **wiring the receiver selection into the add-on
  `settings.xml`** (`avrAddonBackend()` maps DB→add-on enum — Pioneer→`pioneer_eiscp`,
  Sony→`sony_audio_api` configured-but-disabled, custom_command no-op; conservative
  `avr_control_enabled`; new Receiver-control card capturing IP + player input). [PR #110](https://github.com/skull-01/script.oppo203.iso.external/pull/110)
  (merge `bc3ad0e`), tag/release `configurator-v0.5.0` (MSI 3,174,400 B / NSIS 2,071,403 B), now
  holds the repo "Latest". 101 vitest; Pioneer + Sony paths browser-verified; published assets
  re-downloaded byte-identical. No add-on code change (the add-on already ships the AVR settings +
  guarded drivers). Publishing was operator-gated (auto-mode flagged the follow-up release as a
  Create-Public-Surface action) and approved before publish. Updated the §1 header pointer.

- **2026-05-31 (addon functional-flow review + OPPO status probe — EOD)** — operator picked the
  addon area / "Review Addon Functionality" theme, then refined it to a code-verified flow map with
  diagrams. Read the whole add-on flow **first-hand from `resources/lib`** (after an initial pass
  leaned on sub-agents, which the operator flagged as "off"). Outputs: (a) `docs/ADDON_FUNCTIONAL_FLOW.md`
  Mermaid diagrams ([PR #119](https://github.com/skull-01/script.oppo203.iso.external/pull/119) draft, `c6309c0`); (b) a robustness assessment of both architectures that filed
  **7 issues** (#111–#117); (c) on the operator's "I need a function that the OPPO actually played
  the requested file", checked OPPO's RS-232 & IP Control Protocol PDFs and found **`#QFN` (Query
  media file name)** as the documented basis — then built a **read-only status probe**
  (`probe_player_status` + installer menu action + `docs/OPPO_PROTOCOL_REFERENCE.md` + 13 tests;
  [PR #118](https://github.com/skull-01/script.oppo203.iso.external/pull/118) draft, `c9f7579`; pytest 963/3, cov 99%, ruff + mypy clean) and commented the finding on #113.
  Refreshed §3a + §17a; updated the §1 header. Nothing merged to `main`; both PRs are draft pending
  operator review + a Phase-C probe run on real hardware. (Untracked at the repo root and **left
  alone**, not agent-created: `ADDON_RESOURCES_RECONSTRUCTION.md`, `CONFIGURATOR_SRC_RECONSTRUCTION.md`.)
- **2026-05-31 (EOD) — naming-consistency + draft-merge session.** Merged **9 PRs** to `main`
  (HEAD `8c35f28`, 0 open PRs): configurator Sony brand-badge fix (#120), v0.5.0 Step-5 verification
  checklist entry + published-artifact SHA verify (#121), **Sony AVR auto-enable** (#122 — Step 5
  captures PSK + ack + URI; `mapping.avrSettings` emits the `sony_avr_*` keys and enables
  `sony_audio_api` only when complete), and a **naming-consistency sweep** from an audit across
  add-on + configurator + UI: `oppoInput`→`playerInput` (#124), `players.json`→`players-models.json`
  (#125), the `CONFIGURATOR_HANDOFF` mapping (#127), and new `docs/NAMING_CONVENTIONS.md` +
  historical "naming note" flags (#128); addon **TV backend modules renamed `tv_*`** for parity
  with `avr_` (#126 — ~15 files incl. the `_BUCKET` alias-finder / `mypy.ini` / `pyproject.toml` /
  `lib_buckets.py` / tests; bodies unchanged). Also **landed the two prior-session addon drafts** —
  read-only OPPO status probe (#118, resolving a docs-only checklist merge conflict) +
  functional-flow diagrams (#119). Filed `type:bug` **#123** (pre-existing `ruff format` drift on 3
  test files — the only CI "Lint and format" red; spawn-task chip queued). Post-merge `main` green:
  addon pytest 963/3, coverage 99%, mypy 49/0, ruff check clean; configurator 103 vitest + build.
  Refreshed §1 header, §3a, §3b, §17a; saved memories `diagram-output-preference`,
  `configurator-control-tests-are-mocked`, `configurator-avr-db-no-consistency-guard`. (Untracked +
  left alone: `.claude/launch.json` [local preview dev-config], the two `*_RECONSTRUCTION.md`.)

- **2026-05-31 (EOD, later) — robustness bug-fix session + `done for the day`.** `resume` → env
  preflight all green (row 11 MSVC is a vswhere-confirmed false negative — saved to memory) →
  operator picked **Addon: robustness bugs**. Grounded the 6 robustness issues, produced a canonical
  plan (Go granted), and shipped **5 pushed draft PRs** covering **all 7 open addon `type:bug`**:
  **#129** `hold_playback` bounded holds + verbose_push QPL fallback (#112/#115/#116, `a16a4f4`),
  **#130** default `hold_mode`→`tcp_qpl_poll` (#114, `5954556`, merge after #129), **#131**
  self-healing sentinel (#117, `293015e`), **#132** diag probe 80→436 (#111, `bb34919`), then on a
  follow-up ask **#133** ruff-format the drifted test files (#123, `6b920fd`). Each gated (pytest
  green, serial cov 99%, ruff + `ruff format --check` clean, mypy 49/0); SHA-commented + Phase A/C
  checklist rows (prepended to avoid 5-PR collisions); **software-verified only, no hardware.** One
  slip caught: PR C's first commit landed on PR B's branch → cherry-picked it to its own branch +
  reset PR B's local branch to origin (so `#130` on origin stayed clean). Honest finding on #123:
  only 2 of the 3 named files actually drifted. Refreshed §1 header, §3a, §17a, §19; saved memories
  `gh-powershell-json-gotchas`, `env-msvc-row11-false-negative`. `main` untouched; **operator merges
  (#130 after #129) + Phase-C + closes**. §3b (configurator) and §3c (teaching-commentary) untouched.
- **2026-05-31 (EOD, latest)** — AVR follow-ups + `merge everything` + two-playback-chains session
  (configurator-heavy). On `resume` the operator picked **AVR follow-ups**: shipped **#134** (AVR DB
  consistency vitest) + **#135** (Step-5 reachability probe reusing the generic `tv_port_probe`).
  Then **`merge everything`** merged the prior session's 5 robustness drafts **#129–#133** to `main`
  (the 7 `type:bug` fixes; union-resolved the checklist collisions; `#130` was a draft → `gh pr ready`
  first; `ruff format` CI red now clean). Then a new operator-directed theme **two playback chains**:
  **#136** (Step-0 `topology` picker) + **#137** (topology-aware flow + Receiver chain node + pure
  helpers) + **#138** (mapping writes `avr_power_on_enabled`/`avr_restore_*`, gates `tv_switching`
  off in the AVR chain). 8 PRs merged total; **0 open PRs**; `main`@`2ae4b16` green (configurator 123
  vitest + build; addon 976/3, ruff clean). No add-on code change (all AVR settings pre-existed).
  Process notes: a bash heredoc parse error and an over-broad `git add -A` (swept the 3 pre-existing
  untracked files) were both caught and fixed → switched to file-based patch scripts + explicit
  `git add <paths>`; each PR built off fresh `main` and merged before the next. Updated
  [[configurator-avr-db-no-consistency-guard]] (guard now exists). Refreshed §1 header, §3a (bugs now
  merged-but-open), §3b, §17a, §19. **7 addon bugs stay OPEN awaiting operator Phase-C + close.**
  §3c (teaching-commentary) untouched — still PAUSED, now needs a rebase onto current `main`.
- **2026-05-31 (EOD) — DB growth + developer debug view.** Merged **4 configurator PRs** to
  `main`@`9419bea` (`resume` → Configurator theme 1, then AVR-DB growth, TV-DB growth, a planned
  developer debug view, then `merge all`): [#139](https://github.com/skull-01/script.oppo203.iso.external/pull/139) Step-5 restore-input field,
  [#140](https://github.com/skull-01/script.oppo203.iso.external/pull/140) AVR DB +15 `validated:false` 2026 rows, [#141](https://github.com/skull-01/script.oppo203.iso.external/pull/141) TV DB +28 2026 rows + a new
  `tv_db_consistency.test.ts` two-copy guard, [#142](https://github.com/skull-01/script.oppo203.iso.external/pull/142) developer debug view. Merged locally
  `--no-ff`; the recurring Phase-A checklist-row collision was union-resolved each time, plus one
  `step5.tsx` import conflict (kept `isAvrChain` + routed `invoke` via `../ipc`). Post-merge `main`
  green (configurator `tsc` + `vite build` + **146 vitest**). Refreshed §1 header (last sync →
  `9419bea`) + §3b + §19. **§3a (addon) untouched** — configurator + docs only, addon stays 976/3.
  **No issues opened/closed/retitled → §17a cache unchanged.** All new DB rows `validated:false`
  (operator fact-check) with Phase-A/C rows in the checklist. 3 pre-existing untracked files
  (`.claude/launch.json`, two `*_RECONSTRUCTION.md`) left uncommitted (not agent-made this session).
- **2026-06-01 (EOD)** — SVM3 four-option playback architecture, **both areas** in one
  operator-directed session. Unzipped + understood the build-plan bundle, produced a canonical-format
  plan (Go-gated; decisions locked via AskUserQuestion), then built **Session A** (3 stacked addon
  draft PRs #143–#145: `playback_monitor_mode`+preset, `OppoSvm3PlaybackMonitor`, shared
  `run_playback_session()`) and **Session B** (4 stacked configurator draft PRs #146–#149:
  Playback-mode step + renumber, choice+emit triple, SVM3 probe, final-test status split). **Nothing
  merged — `main` code unchanged at `1a1aae6`; all 7 PRs are drafts.** Refreshed the header (last
  sync), §3a, §3b, §19. Memory: added `playercorefactory-two-generators`. **No issues
  opened/closed/retitled → §17a cache unchanged** (3 `area:addon` ENH issues recommended for the
  operator to file; new settings key authorized in-session). 3 pre-existing untracked files left
  uncommitted (not agent-made). Software-verified only; SVM3 **not** hardware-validated.
- **2026-06-01 (EOD #2)** — Big delivery session from `resume`. **Merged all 7 SVM3 stacked PRs**
  (#143–#149 → `main`), filed addon ENH **#150/#151/#152** (SHA-commented), and shipped the
  **six-option `http_handoff`** routing as 4 PRs (#154/#155/#156/#157 — addon presets+launch reusing
  the existing OPPO HTTP fns, configurator pill+payload). Opened wire-transcripts **draft #153** (raw
  OPPO bytes in the dev panel). Produced + Go-gated a combined plan for http_handoff + a
  **live-session-dashboard** Theme 2 (Theme 2 not started). Final gate on `main`@`72c84d8`: addon
  1045/3 + cov 99% + mypy 51/0; configurator 158 vitest + build. Refreshed header / §3a / §3b / §17a /
  §19. Memory: corrected `stacked-pr-local-merge-status` (retarget-to-main is blocked once merged, so
  upper stacked PRs unavoidably show "Closed"; Theme-1 was merged non-stacked off fresh `main` for clean
  badges). `http_handoff` path-translation + mount endpoints + all hardware behavior remain
  operator/Phase-C; **not hardware-validated.** Same 3 pre-existing untracked files left uncommitted.
- **2026-06-01 (EOD #3)** — Two sequential themes this session, both shipped as **draft stacks
  (0 merged; `main` code unchanged at `72c84d8`).** (1) Configurator **Theme 2 — Live Session
  Dashboard**, built as stacked draft PRs [#158](https://github.com/skull-01/script.oppo203.iso.external/pull/158)/[#159](https://github.com/skull-01/script.oppo203.iso.external/pull/159)/[#160](https://github.com/skull-01/script.oppo203.iso.external/pull/160):
  device liveness (reuse `tcp_probe`/`oppo_query`), current-session panel (read
  `oppo203iso-status.json` via the existing SSH/SMB read cmds), and a gated live `#SVM 3` verbose
  stream (new Rust `LiveMonitor` `std::thread`, `oppo-live` events, `canStartLiveStream`
  dual-subscriber gate + auto-stop, no new crate). Gate `tsc` / **173 vitest** / `cargo` 2 / `build`
  green. (2) Operator-directed **pure-agent addon issue audit**, stacked draft PRs [#161](https://github.com/skull-01/script.oppo203.iso.external/pull/161)/[#162](https://github.com/skull-01/script.oppo203.iso.external/pull/162)/[#163](https://github.com/skull-01/script.oppo203.iso.external/pull/163):
  per-issue confirmed-fixed evidence + Phase-C runbook in `docs/audit/` for #111/#112/#114–#117/#123
  + #150/#151/#152 + #113; **#113 flagged partial** (svm3 yes, legacy hold-only). Docs only (empty
  `resources/` diff); cited tests **93 pass**; `ruff format` clean; full addon suite **1045/3**.
  Refreshed header / §3a / §3b / §19. No issues opened/closed/retitled → §17a cache unchanged. Same
  3 pre-existing untracked files (`.claude/launch.json`, two `*_RECONSTRUCTION.md`) left uncommitted
  (operator scratch). Merge both stacks **bottom-up** per [[stacked-pr-local-merge-status]].

- **2026-06-01 (EOD #4)** — Resumed; operator picked **addon Phase C** + configurator **theme 1**, then
  **"Merge all".** Landed **7 PRs**: dashboard D1 [#158](https://github.com/skull-01/script.oppo203.iso.external/pull/158)
  `5755184` → D2 [#164](https://github.com/skull-01/script.oppo203.iso.external/pull/164) `e4118c0` → D3
  [#160](https://github.com/skull-01/script.oppo203.iso.external/pull/160) `e8d35bf`; audit
  [#161](https://github.com/skull-01/script.oppo203.iso.external/pull/161) `fdd3368` /
  [#162](https://github.com/skull-01/script.oppo203.iso.external/pull/162) `a543615` /
  [#163](https://github.com/skull-01/script.oppo203.iso.external/pull/163) `e957aab`; wire-transcripts
  [#153](https://github.com/skull-01/script.oppo203.iso.external/pull/153) `832b76e`. `main`@`9b0cb6d`,
  **0 open PRs.** Configurator gate `tsc` / **175 vitest** / `cargo test` 5 / `build` green; addon
  `resources/` untouched → **1045/3**. **Lesson 1:** stacked `--delete-branch` CLOSES the child here (no
  auto-retarget) — it closed [#159](https://github.com/skull-01/script.oppo203.iso.external/pull/159)
  (recovered as #164); fix is retarget children to `main` *first* (proven on the audit stack).
  **Lesson 2:** a duplicate `#[cfg(test)] mod tests` from a Rust auto-merge is invisible to `cargo check`
  — `cargo test` caught the `E0428` on #153. Corrected the §3b theme-1 "auto-retarget" claim; rewrote
  memory [[stacked-pr-local-merge-status]] + added [[rust-duplicate-mod-tests-on-merge]]. Refreshed
  header / §3a / §3b / §19; flipped all 7 checklist rows to merged; annotated #159 → #164. No issues
  opened/closed/retitled → §17a cache unchanged.
- **2026-06-01 (EOD #5)** — Resumed; operator picked **Configurator theme 3** (dashboard follow-on), then
  **"go"**, then **"file the matching"**. Built a 2-PR "dashboard memory" stack (**nothing merged**):
  [#165](https://github.com/skull-01/script.oppo203.iso.external/pull/165) `9b15e93` **settings-snapshot
  diff** (Configuration changes card; new Rust `read_app_json`/`write_app_json` `safe_app_rel`-guarded
  store + exported `parseSettingsXml` + `settings_diff`/`dashboard_snapshot`/`dashboard_store`; secret ids
  masked via shared `isSensitiveKey`) → stacked
  [#166](https://github.com/skull-01/script.oppo203.iso.external/pull/166) `1408eab` **session log**
  (Session history card; pure `session_log.foldObservation`, deduped + capped-50). Filed ENH **#167/#168**
  (`area:configurator`), SHA-commented + left open; updated both PR bodies to "Tracks #167/#168" + added 2
  checklist Phase-A/C rows (PR-166 branch `6f20834`). Gate on the PR-166 tip: `tsc --noEmit` 0 / **194
  vitest** (+19) / `cargo test` 8 (+3 `safe_app_rel`) / `vite build`; addon `resources/` untouched → 1045/3;
  no new crate dep; frozen guards held. Refreshed header / §3b / §17a (rows #167/#168, now **16 open**, open
  PRs → #165/#166) / §19. **§17a:** 2 issues opened (#167/#168). One theme, 2 PRs (within the ≤4 cap).
- **2026-06-01 (EOD #6)** — Guided-install initiative (very large). Overwrote §3a (add-on = release-only:
  `v2.9.14-experimental` cut off `main`, no `resources/` change) + §3b (configurator install / SSH-first flow
  / Roku switch across 4 branches `cfg-phase1-install-addon` / `cfg-phase2-ssh-first-flow` /
  `cfg-phase3-hdmi-switch` / `cfg-experimental3-integration`; 3 draft PRs #170/#171/#172; pre-releases
  `configurator-v0.6.0-experimental2`+`experimental3`). Re-synced header to `main`@`1c81f2c`. Merged #169
  (six-preset guard) + added the "six playback-architecture presets are a maintained matrix" norm to §4.
  Rewrote `docs/BUILD_PLAN.md` for the initiative. **All hardware paths software-verified only.**
- **2026-06-02 (EOD #7)** — Merged the guided-install initiative (#170/#171/#172) to `main` via the
  experimental3 integration branch (`b927b33`; configurator 0.6.0). Built Phase 1b NAS-path capture
  (observe-and-verify, D-4, issue #173) as draft #174; resolved **D-2** (user-supplies ISO + placeholder)
  + **D-3** (`Addons.SetAddonEnabled` + manual-restart fallback) in `docs/BUILD_PLAN.md`; built D-3 as
  draft #175. Refreshed the header (`main`@`7554c15`) + §3b (EOD #7 block + resume list). Added memory
  `oppo-ip-protocol-no-playing-path`. **All hardware paths software-verified only; PR-4.2 (D-2 copy) is
  the resume point.**
- **2026-06-02 (EOD #8)** — Operator drove "build all of guided-install Phases 3/4/5" off `resume`
  (full auth, merge-as-I-go, finer PRs, file ENH issues). Built + merged **13 PRs**: foundation
  #174/#175; backend layer #177/#179/#181/#183; UI layer #184/#188/#185/#187/#190/#186/#189 (the 7 UI
  PRs via **3 parallel sub-agents in worktrees**). Then operator "**close the verification queue, keep
  the checklist**" → closed **23** confirmation-queue issues (kept `MANUAL_VERIFICATION_CHECKLIST.md`);
  and "**fully wire everything**" → audited (all 32 Tauri commands UI-wired, no stubs) + fixed the
  TV-backend config-persistence gap (#198/#199). Refreshed the header (`main`@`2a4e4af`), §3a/§3b, §17a
  (queue cleared → 5 open), `docs/BUILD_PLAN.md` + the checklist. Added memory `worktree-junction-npx-tsc`.
  **Combined gate green (tsc / 261 vitest / build / cargo 37 / addon 1046·3 / mypy 51·0 / cov 99%); all
  software-verified only — operator Phase-C hardware validation is the only remaining work.**
- **2026-06-02 (EOD #9)** — `resume` → operator **"do all cfg"**. Grounding found **#103/#105 already
  implemented** on `main` (evidence-commented + checklist note, `516d465`). Built the **dashboard-memory
  stack** [#200]→[#201]→[#202] (#167/#168, with exact `session_id` dedup); then **[#203]** shared
  playback-preset source (cross-area parity guard), **[#204]** TV DB +26 China TCL/Hisense models under a
  new `CN` region + a `tv_ip` comment fix, a **build-plan refresh** (`d1fe1dc`), and a **fullwired audit**
  (configurator↔add-on confirmed fully software-wired). Refreshed the header (`main`@`d1fe1dc`) + §3a/§3b.
  **6 draft PRs queued, 0 merged; all software-verified only — Phase-C the only remaining work.** §17a
  unchanged (no issues opened/closed/retitled — 5 still open). No new memory added.
- **2026-06-02 (EOD #10)** — Releases + next-theme planning session. Merged the 7-PR
  configurator queue (#200–#204; stale #165/#166 closed), then cut **add-on `v2.9.14`** (via
  `/release` + `package.yml`) and **configurator `v0.7.0`** (manual `npm run dist` MSI/NSIS;
  holds the repo "Latest" badge; bundles v2.9.14). Then planned + **saved the Pure-HTTP/436
  initiative (PRs 1–6) to `docs/BUILD_PLAN.md`** (Active initiative) and queued it as the next
  theme in §3a/§3b. Refreshed the header Last-sync + Tests (`main`@`c200349`; addon 1053/3,
  configurator 290 vitest / cargo 40) + §17a. Added memory [[configurator-release-is-manual]].
  Pre-existing untracked files (`.claude/worktrees/` junctions, reconstruction `.md`s) left
  uncommitted on purpose (not this session's work).
- **2026-06-02 (EOD #11)** — Xnoppo V3 / Pure-HTTP-436 SHIPPED. Saved
  `docs/XNOPPO_V3_ADOPTION_AND_DECISION_TREE_ENHANCEMENTS.md` (grounded plan), built + merged all
  6 PRs (#208/#210/#212/#214/#216/#218) to `main`, and cut stable add-on `v2.9.15` + configurator
  `v0.8.0`. Overwrote §3a/§3b (EOD #11, clean stopping points), refreshed the header Last-sync +
  Tests (`be196ac`; addon 1132/3, configurator 294 vitest), and §17a. Added memories
  [[xnoppo-v3-pure-http-shipped]] + [[serial-only-monkeypatch-target]]; bumped
  [[configurator-release-is-manual]] to the v2.9.15/v0.8.0 precedent. Pre-existing untracked files
  left uncommitted on purpose.
- **2026-06-03 (EOD #12)** — Full-audit remediation + TV-DB growth + reset-all + installer
  old-version check. Ran a 7-agent full audit over both areas; fixed + merged **all 30 findings**
  across 7 PRs (#225/#234/#238/#245/#253/#255/#257 — addon A1/A2/A3/H2/L12 + configurator C1/C2)
  with ~27 `type:bug` issues filed + SHA-commented + OPEN. Then TV DB **+110** TCL/Hisense rows
  (#258, 350→460), the **Reset-all-configurations** action (#260), and an **installer old-version**
  NSIS PREINSTALL hook (#262). Cut **configurator v0.8.1 / v0.8.2 / v0.8.3** (manual `npm run dist`;
  v0.8.3 holds "Latest"; all bundle add-on v2.9.15). Overwrote §3a/§3b (EOD #12, clean stopping
  points), refreshed the header Last-sync + §17a, and bumped [[configurator-release-is-manual]]
  with the standing "a bare release = the configurator release" rule + the v0.8.1/0.8.2/0.8.3
  precedents. Gate: addon 1155/3 · serial coverage 99% · mypy 51/0; configurator tsc 0 · 301
  vitest · cargo · vite build. 0 open PRs. Pre-existing untracked files left uncommitted on purpose.
  **Post-EOD:** operator flagged the **Reset-all button as effectively unreachable** (renders only on
  the dashboard, reachable only after completing the wizard/test) → filed **#263** (`type:bug`,
  `area:configurator`) and surfaced it as the **next configurator resume theme** (make reset reachable
  from the shell/Step 0; ship v0.8.4). Not built this session per operator direction.
- **2026-06-03 (EOD #13)** — Built the queued **#263** Reset-all reachability fix and shipped it.
  Operator: `resume` → Configurator → #263 → "go" (build) → "go" (ship). New `reset_all` screen
  reusing `ResetAllCard` unchanged, surfaced from a persistent app-header button (every screen) + a
  Step 0 link; `steps.ts` + a pure `steps.test.ts`. PR #264 (`285b5e3`, merged `473df58`) → bump PR
  #265 (merged `f437567`) → release **configurator-v0.8.4** (holds "Latest"; MSI 3,682,304 B + NSIS
  2,542,219 B + SHA-256, bundles add-on v2.9.15). Overwrote §3b (EOD #13, clean stopping point; §3a
  untouched — no addon work), refreshed the header Last-sync + Latest-release lines + §17a. Gate: tsc 0
  · 304 vitest · vite build · tauri release build; browser-verified the nav. #263 SHA-commented + OPEN
  (Phase-C pending). 0 open PRs. Pre-existing untracked files left uncommitted on purpose.
- **2026-06-03 (EOD #14)** — Long configurator session off `resume`. Shipped **v0.8.5** (reset-all
  hang fix + live progress, #266/#267), a **7-theme infra/hardening batch → v0.8.6** (repo hygiene
  #271; the configurator's **first GitHub Actions CI + tag→release automation** #272; diagnostics
  export #273; single-prompt installer #274; add-on property tests + a real `OverflowError` fix
  #275/#276; i18n scaffold #277; bump #278), and **v0.8.7** (Hisense E8N Pro #280, hid the Step-0 "Not
  yet" button #281, TV family Sizes display #282, bump #283 → CI-published). Plus the **OPPO HTTP
  command catalog** (#285, tester-contributed), a **regenerated `docs/BUILD_PLAN.md`** (#286/#287), and
  the **Developer Options console plan LOCKED + queued** as the next configurator theme (#288). Doc
  updates this cycle: prepended the §8 EOD #14 Last-sync entry; §3b now leads with **▶ NEXT THEME
  (Developer Options, locked)** then the EOD #14 + v0.8.7 entries; §3a untouched (the add-on
  OverflowError fix is captured in the EOD #14 batch). Extended memory [[gh-powershell-json-gotchas]]
  (a PowerShell here-string mangles `gh --body`/`git commit -m` → use `--body-file`/`-F`). All
  software-verified; **0 open PRs**; `main`@`eec9edf`. Releases are now `git tag configurator-v*` → CI.
- **2026-06-03 (EOD #15)** — Built the entire **Developer Options console** initiative (#290) in one
  session: 7 PRs (#298 shell, #299 OPPO, #300 Kodi, #301 TV, #302 AVR, #303 NAS, #304 Kodi-scan) + bump
  #305, all merged to `main` and CI-gated; tagged **`configurator-v0.9.0`** → the CI release job built
  MSI/NSIS + published as Latest (bundles add-on v2.9.15). Rewrote §3b's top entry from the LOCKED
  "next theme" block to the shipped EOD #15 record; marked `docs/BUILD_PLAN.md` §2 ✅ DELIVERED; added a
  Developer-Options Phase-C section to `docs/MANUAL_VERIFICATION_CHECKLIST.md`. New configurator Rust
  commands: `oppo_http_get`, `install_addon_zip`, `kodi_restart`, `tv_sony_bravia_ircc`,
  `scan_nas_hosts`, `nas_test_login`, `scan_kodi_hosts` (cargo 47→50; vitest 328→338). `main`@`c3b8bcf`;
  **0 open PRs**.
- **2026-06-03 (EOD #16)** — Shipped the **AutoScript helper** (#306) as the 6th Developer Options
  sub-section: 3 PRs (#310 generator/contract, #311 panel + Desktop export, #312 telnet) + bump #313;
  tagged **`configurator-v0.9.1`** → CI built MSI/NSIS + published as Latest. New cross-language guard
  `tests/test_autoscript_consistency.py` (the configurator AutoScript generator mirrors the add-on's
  `autoscript_helper.generate()` byte-for-byte, pinned by `autoscript-fixtures.json`). New configurator
  Rust cmds: `export_autoscript_bundle` (Desktop folder), `autoscript_telnet_check`,
  `autoscript_push_telnet`. Rewrote §3b's top entry to the EOD #16 record; noted the AutoScript helper
  delivered under `docs/BUILD_PLAN.md` §2; added an AutoScript Phase-C section to the checklist.
  `main`@`02f44bf`; **0 open PRs**.
- **2026-06-03 (EOD #17)** — Shipped **Developer Options UX refinements** (#314) from operator feedback:
  3 PRs (#318 side-by-side `.dev-split` transcript layout, #319 Browse + add-on identity validation
  gate on the Kodi upload, #320 TV HDMI input switch via `planSwitch`) + bump #321; tagged
  **`configurator-v0.9.2`** → CI built MSI/NSIS + published as Latest. New configurator Rust cmds
  `validate_addon_zip` + `pick_addon_zip` (new dep `rfd`). Rewrote §3b's top to the EOD #17 record;
  noted under BUILD_PLAN §2; added the refinements' Phase-C section to the checklist. `main`@`07a3f3f`;
  **0 open PRs**.
- **2026-06-03 (EOD #18)** — Shipped the **embedded add-on build tag** (#322, the deferred v0.9.2
  follow-up): PR #325 (add-on packaging stamps `resources/oppokodiaddon.sig`, a SHA-256 content
  manifest; `compute_manifest_sig`) + PR #326 (configurator `validate_addon_zip` verifies it →
  signed/unsigned/mismatch; Rust `addon_manifest_sig` + dep `sha2`) + bump #327; tagged
  **`configurator-v0.9.3`**. Cross-language guard: `tests/test_addon_signature.py` ↔ a cargo test
  both pin the same fixture hash. New cross-language guard + new configurator dep (`sha2`). `main`@`6266aa7`;
  **0 open PRs**.

- **2026-06-03 (EOD #19)** — Shipped a **quality + capability roll-up** (operator "Do 1 2 3 then 4"):
  (1) dev-console **hardening** from an adversarial review (PR #328 — no blocking issues found; net.exe
  cred sanitize, heredoc-terminator guard, zip-entry read cap, addons-path guard, "build tag verified"
  relabel); (2) an **add-on property-test pass** (PR #330; bug #329) fixing 4 `int()`-coercion crashes in
  `discovery`/`autoscript_helper` (new `_safe_port`; `_safe_int` catches `OverflowError`) +
  `tests/test_property_addon_robustness.py` (optional Hypothesis + curated fallback); and (3) the **AVR
  raw-command console** (PR #332; ENH #331; new Rust `avr_raw_send` — Denon telnet / Onkyo·Pioneer eISCP /
  Yamaha MusicCast HTTP). Bumped + tagged **`configurator-v0.9.4`** (bundles the fixed add-on). Gate: cfg
  `tsc -b` + vitest 356 + cargo 57 + vite build; add-on pytest -n auto 1187/3 + serial coverage 99% + ruff.
  Refreshed §3a, §3b, §17a, §19. New Rust cmd `avr_raw_send`; new dev test file. `main`@`7c9d1d8`;
  **0 open PRs**.

- **2026-06-03 (EOD #20)** — Built add-on **v2.9.16** to the PR stage (operator's **3-theme override**:
  Addon 2 + Cfg 1 + Cfg 2; `done for the day` called mid-release while CI ran). PR
  [#333](https://github.com/skull-01/script.oppo203.iso.external/pull/333) (`release/v2.9.16`, 2 commits
  `b2d83b2` + `e356020`) folds the 7 post-v2.9.15 fixes + the version/test/doc/evidence bump; **all CI
  green, NOT yet merged/tagged/published**. Release verification surfaced + fixed two pre-existing bugs: a
  `discovery._safe_port` mypy `--strict` regression (from #329) and a cross-area **AutoScript CR/LF
  injection** in `autoscript_helper.generate()` (operator chose the **full cross-area fix**: add-on
  `_safe_text` + the `autoscript-gen.ts` mirror + a `crlf_paths` fixture + both consistency guards). Gate:
  add-on pytest 1187/3, serial coverage 99%, mypy 51/0, ruff clean, audit 607/607; cfg tsc/vitest 357/build.
  Refreshed §3a/§3b (EOD #20) + the header + §19. Cfg themes 1 (i18n) & 2 (installer single-prompt)
  grounded but not started. `main`@`5fa1b70` (v2.9.16 not on `main` yet); **1 open PR (#333)**.
  **Resume → merge #333 + tag `v2.9.16` + publish FIRST.**
- **2026-06-03 (EOD #21)** — `done for the day` after the operator's **3-theme override completed
  automatically** (Addon 1 + Cfg 2 + Cfg 3). Addon `v2.9.16` Final and configurator `v0.9.5` BOTH
  shipped + published (v0.9.5 holds "Latest"; v2.9.16 published but intentionally not "Latest").
  Refreshed §3a/§3b (EOD #21), the header (Last sync → `15640a5`, Latest release → v0.9.5/v2.9.16),
  §17a (filed #334), and §19 (this entry). New memory [[configurator-ci-skips-tauri-build]] (the cfg
  PR gate skips `tauri build`; the NSIS template compiles only on the tag — verify locally). Tests:
  add-on pytest **1187/3** (serial coverage 99% per the v2.9.16 CI gate; no add-on code changed this
  session); cfg `tsc -b` / **vitest 359** / `vite build` + `cargo test 57` on CI. `main`@`15640a5`;
  **0 open PRs; working tree clean.** **Resume → operator Phase-C** (v2.9.16 Kodi install; v0.9.4→v0.9.5
  single-prompt upgrade on a Windows host) **or cfg i18n migration** (the remaining grounded theme).
- **2026-06-04 (player-DB enrichment — Protocol 1 run)** — Operator invoked **Protocol 1**
  (full auth; batch decisions up front; execute end-to-end + release). Shipped **add-on
  v2.9.17 Final** + **configurator v0.9.7** (umbrella ENH #341): 5 OPPO-clone variants (M9205
  V2/V3/V4, M9702 Plus, VenPro V203) + a cross-area Dolby Vision data layer
  (`resources/lib/oppo/dolby_vision.py` ↔ `players-models.json`, drift-guarded). Feature #342 →
  add-on release #343 (tag `v2.9.17`) → configurator bump #344 (tag `configurator-v0.9.7`,
  Latest). Refreshed §3a/§3b; added two §4 norms (README front-page + Protocol 1) and the §1
  `protocol 1` trigger row. New memories [[protocol-1-full-auth-autonomous]],
  [[readme-current-status-per-release]]; new guard `tests/test_readme_current_release.py`. Fixed
  the stale README front page (→ v2.9.17 / cfg-v0.9.7) and the configurator release-title
  branding (`configurator-ci.yml` + the v0.9.6 release retitled). Gate: add-on pytest
  **1219/3**, serial coverage **99%**, mypy 51/0, ruff clean, audit PASS 616/616; cfg
  `tsc`/vitest 361/`cargo`/build green. `main`@`4d553d8`. Deferred: a reviewed CI-optimization
  PR (skip claude-review + add-on gate on configurator/`release/*` PRs; skip cfg gate on tags).

---

# §20 Dev notes (operator's verbatim instructions)

_Append-only. Each entry: `### YYYY-MM-DD HH:MM — dev note` followed by the operator's
text VERBATIM. No summarizing, no editing. Added via the `dev note:` trigger._

### 2026-05-31 13:05 — dev note

main's CI is red on ruff format --check — but it's pre-existing and unrelated to these PRs. Three add-on test files (tests/test_all.py, test_players_db_consistency.py, test_v2910_build2_player_taxonomy.py) have formatting drift; ruff check itself passes. None of the merged PRs touch Python, so they neither caused nor worsened it. I've queued a task chip to fix it (one ruff format run + full-suite re-verify, as a draft area:addon PR) — click to spin it off, or dismiss.

---

# §21 Questions log

_Q&A pairs from substantive conversations (clarifying scope, picking between approaches,
defining terminology). Append after each substantive turn. Newest-last._

### 2026-05-28 — Aesthetic + stack + repo layout for the configurator

- **Q:** Which tech stack should we build the configurator in?
  **A:** Tauri 2 (Rust + web UI) — natural port from the React/CSS prototype.
- **Q:** Where should the configurator code live?
  **A:** Subdirectory in this repo (`configurator/`).
- **Q:** Which aesthetic direction?
  **A:** Direction A — Warm Paper (default per design handoff).

### 2026-05-28 — Naming

- **Q:** Is "installer" the right word?
  **A:** No — the Kodi add-on is installed by Kodi; this Windows app *configures* the
  already-installed add-on. Renamed everything to "OppoKodiAddon Configurator" / verb
  "configure" / "set up". Directory `installer/` → `configurator/`.

### 2026-05-28 — Issue model under the new handoff

- **Q:** GitHub Issues, PR-only, or hybrid?
  **A:** Hybrid — Issues for bug/enhancement tracking, PRs for delivery.

### 2026-05-29 — Sequencing ENH-#41 against PR #40; in-add-on guidance hint mechanism

- **Q:** Should ENH-#41 (configurator-owns-config) ship as one PR or be split
  against PR #40 (strip-wizard, still draft)?
  **A:** Split into three parts. **Part A** (policy doc to
  [`AGENTS.md`](AGENTS.md) + [`CONTRIBUTING.md`](CONTRIBUTING.md)) ships now
  from `main` — no overlap with #40's diff. **Parts B** (in-add-on guidance
  hint on settings open) and **C** (settings.xml ownership marker) wait until
  #40 merges; both modify `resources/settings.xml`, which #40 renames
  (`<category id="wizard">` → `<category id="playback">`) and trims
  (`wizard_mode` removed). Doing B + C now would create avoidable merge
  friction.
- **Q:** For Part B's in-add-on guidance hint, which mechanism — a static
  label at the top of `settings.xml`, a `service.py` first-open-per-session
  `xbmcgui.Dialog().notification`, or both?
  **A:** Both. Static label is permanent visible guidance; the notification
  draws attention exactly once per Kodi session (tracked via
  `xbmcgui.Window(10000).setProperty(...)`, which clears on Kodi restart).
  Most code, strongest UX guarantee.

### 2026-05-29 — Merge order + stacked-PR auto-close (the `merge all pending` directive)

- **Q:** With three open PRs (#52 configurator, #54 mypy PR 2, #55 mypy PR 3 stacked
  on #54), what order merges safely?
  **A:** Stacking dictates it: **#54 → #55 → #52.** #55's base branch *is* #54's
  branch, so #54 must land first. #52 is independent (configurator-only) and goes
  last. Verified each was MERGEABLE/CLEAN and CI-green before merging.
- **Q:** What happened to #55?
  **A:** Merging #54 with `--delete-branch` deleted the branch #55 was based on, which
  **auto-closed #55** — GitHub *closes* (does not retarget) a PR whose base branch is
  removed, and a closed PR whose base is gone can't be reopened or retargeted. The
  fix: recreate the identical branch/commits as a new PR (**#56**) against `main` and
  merge that. Confirmed via `git merge-tree` it was 0-conflict and did **not** revert
  `main`'s newer `AI_RESUME_HANDOFF.md` (pr3 never touched that file, so the 3-way
  merge keeps main's copy). **General rule for stacks:** retarget the child PR to
  `main` *before* deleting the parent's branch, or expect the recreate dance.

### 2026-05-30 — ENH-#51 rollout scope ("do all of these" → how far in one session)

- **Q:** On `resume` the operator picked **both** ENH-#51 candidate themes at once — "PR 4
  (import-fallback strategy for the no-redef idiom modules)" **and** "the cascade group" —
  with "do all of these". One theme or many PRs?
  **A:** One theme (ENH-#51), delivered as a stack. The cascade group is blocked on the two
  un-migrated hubs (`settings_reader` 72 + `oppo_control` 111 errors), so the real sequence is
  PR 4 (leaves) → PR 5 (hubs) → PR 6 (cascade) → PR 7 (the larger hub-dependent idiom modules
  oppo_remote/external_player/installer/preset_manager). Four PRs — at §4's soft cap.
- **Q:** After PRs 4+5 (the hubs unblock everything), the remaining work was ~425 strict
  errors / 11 modules — larger than the two bullets implied. Continue now or checkpoint?
  **A:** Operator chose **"everything now (PR 6 + 7)"** (popup). Proceeded; parallelized the
  mechanical per-module annotation across general-purpose sub-agents to fit it in one session
  while keeping verification (gate + full suite + coverage + diff review) on the main thread.
