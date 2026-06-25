# opporepomerge

A consolidated mono-repo that folds **four** related Oppo/Kodi add-on projects into one tree, preserving each project's full git history (740 commits) under namespaced subdirectories and per-repo `<subdir>/<branch>` branches.

Every project here is chasing the same goal from a different angle: hand **OPPO disc-style media** (ISO images and `BDMV`/`VIDEO_TS` disc folders) off from Kodi to an external OPPO-class player so the disc plays on real OPPO hardware — and do it **without the pre-play "blip"** (Kodi starting to decode and then yanking the file back) and **without corrupting HDMI-CEC** on a TV bus that other devices share. The recurring villain across all four lineages is CEC: there is no clean "give the input back" primitive, and the only spec-legitimate way to move the TV is to let each device announce *its own* active source. Everything else in this story is the wreckage of learning that the hard way.

---

## What's inside

| Subdirectory | Source repo | Add-on id(s) | Version |
|---|---|---|---|
| [`script.oppo203.iso.external/`](script.oppo203.iso.external/) | [skull-01/script.oppo203.iso.external](https://github.com/skull-01/script.oppo203.iso.external) | `script.oppo203.iso.external` (+ Tauri/React Windows configurator) | 2.9.17 / configurator 0.9.15 |
| [`OppoKodiBridge/`](OppoKodiBridge/) | [skull-01/OppoKodiBridge](https://github.com/skull-01/OppoKodiBridge) | `service.oppokodibridge` | 2.0.14 |
| [`OppoKodiBridge-v3/`](OppoKodiBridge-v3/) | [skull-01/OppoKodiBridge-v3](https://github.com/skull-01/OppoKodiBridge-v3) | `service.oppokodibridge.v3` | 3.1.0 |
| [`CEC-Control-Experiment/`](CEC-Control-Experiment/) | [skull-01/CEC-Control-Experiment](https://github.com/skull-01/CEC-Control-Experiment) | `service.oppokodibridge.cec` + `script.cecreclaim` | 0.4.5 / 0.1.0 |

The hardware chain under test throughout is: **Kodi on an Ugoos AM6B+ (CoreELEC)** → an **M9205/M9207 OPPO clone** (a UDP-203-class player) controlled over a reverse-engineered HTTP app API → a **TCL Q9L Pro** TV, switched by HDMI-CEC.

---

## The journey

This is the part the repo exists to record: the real engineering chronology, including the dead ends and *why* they were abandoned.

### Act I — OppoKodiBridge v2: the bridge and the CEC-bus wars (`service.oppokodibridge`, 2.0.x)

v2 was a deliberate clean-slate restart (`461d9de`). It threw out v1's broad hardware support — the Windows configurator, per-brand TV backends, the 7-preset matrix — to support exactly **one** chain. A Kodi service intercepts local playback and hands the disc off to the OPPO. It shipped software-verified only (16 pure-logic tests), explicitly **not** hardware-validated.

The early scaffold (2.0.0–2.0.2) reused v1's OPPO API, and it simply **did not work** on the M9205 clone. The OPPO layer was rewritten from scratch at **2.0.5** (`9506f2b`) to mirror the operator's working `emby-chinoppo-bridge`: `/signin`, `/loginNfsServer`, `/mountNfsSharedFolder` (mounts at `/mnt/nfs1`), `/playnormalfile` addressing the file as `/mnt/nfs1/<basename>`. That rewrite surfaced the first genuinely surprising fact:

- **The OPPO's NFS server is *not* the Kodi NAS IP.** The same TrueNAS content is exported twice on different subnets — Kodi sees `nfs://192.168.1.177/...`, but the OPPO must use its *own* server `192.168.10.20` exporting `srv/nfs/media`. The server is auto-resolved by asking the OPPO itself (`/getdevicelist`, the `sub_type:nfs` entry), never hand-configured. Using the PC-side address is the most common mistake.
- **RS-232/IP control physically cannot play a file by path.** The documented `#XXX` 3-letter control protocol (TCP `:23` / RS-232) is a remote-control replacement — no command takes a path or URL. Only the reverse-engineered HTTP app API on TCP `:436` can start a specific network file. This single limitation forces the whole architecture: playback is *always* HTTP, regardless of the serial option.

Playback was first confirmed live at **2.0.6** (`a2a5392`), which wired in the **wake-and-init dance**: the `:436` API sleeps after boot and is woken by a UDP datagram `b'NOTIFY OREMOTE LOGIN'` to `:7624` (not an HTTP call, not a `0x55` packet, not broadcast), retried until `:436` opens; then a required `firmware → setupmenu → signin → globalinfo` handshake runs, of which **signin is the load-bearing step**.

Two brutal gotchas landed here:

- **Mounting a non-exported folder HARD-CRASHES the OPPO** — it kills both `:436` and `:23` and needs a mains power-cycle to recover. You may only mount a real export from `/getNfsShareFolderlist` (or a subfolder of one). A stuck `bd_is_playing` also blocks mounts, so a `STOP` must precede them.
- **Blu-ray disc folders are started by `checkfolderhasBDMV`** — the OPPO won't play `index.bdmv` directly, so for disc-structure paths the handoff mounts the parent, sends `STOP`, then calls `/checkfolderhasBDMV`, which on this clone doesn't just *check*, it *starts* the disc (2.0.8, `274dea7`, verified with the Ant-Man 4K Blu-ray).

**TV switching is where v2 went to war.** Switching the TCL to the OPPO's input means the OPPO has to assert CEC active source — and it only does that on a **power-ON transition**, never when it starts playing while already on. So the handoff power-cycles the OPPO (`#POF → #PON`) before waking the API (2.0.7, `ff72988`), costing ~24s per play (mostly the OPPO's unavoidable boot-for-playback time). Reclaim on stop = Kodi's `CECActivateSource`. To kill that ~24s, two faster-switch attempts were tried and **both reverted**:

1. **CEC attempt #1 — `cec-client` broadcast (2.0.9, `a61fa18`).** Broadcasting `<Active Source>` (`tx 4F:82:10:00`) instantly switched the TCL — but `cec-client` opens a *second* libCEC client and corrupted Kodi's own CEC: the stop-reclaim stopped working and the input kept getting re-grabbed. Reverted in 2.0.10 (`4c5d8c8`).
2. **CEC attempt #2 — `aocec` sysfs inject (2.0.12, `30fca1c`).** The Amlogic sysfs route (`echo 4f 82 10 00 > /sys/class/aocec/cmd`) avoided the second-client problem and switched the TV — but the injected `<Active Source>` frame carries a **spoofed initiator logical address (4)** that collides with other devices, and a **Mi Box S on a different HDMI input got cross-controlled**. Reverted in 2.0.13 (`5b88144`).

The durable conclusion, baked into `DEV_NOTES.md` (`cbcfcb7`): **never inject CEC active-source on a shared bus.** Only a device announcing its *own* source (the OPPO's One-Touch-Play) is safe. Faster TV switching via CEC injection is **closed**.

v2 also added a **disc-only handoff filter** (2.0.11, `eb70e4d` — the published "Latest"): only `.iso` and disc folders (`BDMV`/`VIDEO_TS`/`HVDVD_TS`) route to the OPPO; everything else (MKV, MP4, a *loose* `.m2ts`) plays in Kodi. A serial RS-232 transport (2.0.14, `44d193f`) was a modest win — a more reliable transport for *power* commands only; playback stays HTTP. The hardware lessons that come with it are concrete: on kernel 4.9.269, the **Flirc is a receiver, not a blaster**, and the **Prolific PL2303-GC (`067b:23a3`) is unusable** (`pl2303_vendor_write -32`; data never flows) — use a **CH340/CH341 or FTDI** adapter instead. (The OPPO answers `#QPW → @OK ON` over IP, proving the adapter is the culprit, not the OPPO's RS-232. Note: the two internal docs label that chip differently — `DEV_NOTES.md` says "ATEN," `OPPO_PLAYBACK_PROTOCOL.md` says "HXN".) The documented end-state recommends an **external network IR blaster (Broadlink RM4 mini)**, off the CEC bus entirely, as the pragmatic winner.

### Act II — OppoKodiBridge v3: the playercorefactory fork that killed the blip (`service.oppokodibridge.v3`)

v3's founding pivot (3.0.0, `5a7a09c`) fixed v2's worst UX flaw: the **blip**. v2 let Kodi *start* the disc and then yanked it back to hand off — a visible "Kodi plays, then hands off" stutter. v3 instead writes a persistent `playercorefactory.xml` that routes `.iso`/`BDMV`/`VIDEO_TS` to an **external player process** (`pcf_player.py`) *before* Kodi's own player ever touches the file. No decoding starts, so there is no blip. The non-obvious cost: Kodi reads `playercorefactory.xml` only at startup (before any add-on runs), so the service can't set it up just-in-time — it writes the file and leaves it, and a **fresh install needs one Kodi restart**. It shipped CEC-free by design with **no** CEC reclaim and IR as the intended switch; when no IR is configured it falls back to an interim OPPO power-cycle.

Stop-detection became **two-phase**: a latency-tolerant HTTP `/getglobalinfo` poll while the NFS mount + buffer spin up, then a verbose `#SVM 3` TCP connection on `:23` where the OPPO **pushes** `@UPL STOP/HOME` the instant it happens. The HTTP fallback is **tri-state** (playing / idle / unknown) so a transient blip is never mistaken for a stop, and it's bounded so it can never hang and skip the reclaim.

### Act III — the IR detour

To switch the TV CEC-free, a complete **Broadlink RM4 mini IR path** was built and merged (PR #1, `1567daa`; the full path lives at `5bfdf15` on the `OppoKodiBridge-v3/ir-blaster-integration` branch). The engineering here was real: rather than vendoring upstream `python-broadlink` (which hard-imports the `cryptography` C-extension CoreELEC **lacks**), a ~330-line stdlib-only client (`broadlink_rm4.py`) was hand-rolled, plus a **vendored pure-Python AES-128** floor pinned by a **FIPS-197 known-answer test** (the add-on ships as a runtime-only zip with no pip, so every dependency must be vendored). Sequencing/reliability live one layer up in `ir.py`; the IR send was re-timed to fire the instant the OPPO first reports `PLAYING`, on a daemon thread so a multi-key nav sequence can't delay the stop-watch. 47 off-box tests green, hardware never validated.

An adversarial multi-agent pass over 24 load-bearing facts **refuted two** — and one of them reopened the whole story:

- The **Mi Box cross-control was NOT inherent to CEC.** It came specifically from the Kodi box spoofing a *foreign* `<Active Source>` frame via the Amlogic driver (`/sys/class/aocec/cmd`). A device announcing its *own* source is legitimate — which made pure CEC viable again.
- The **TCL Q9L Pro runs TCL's China-only Lingxi/LingControl OS, not Google TV**, so no published platform code set could be trusted; capture-on-hardware became the only safe path. (The TCL remote also has no discrete-HDMI button — Source → arrows → OK over a list — forcing an end-stop-anchored, idempotent nav-sequence design.)

A subtle, hardware-free bug nearly buried the whole effort: `config.from_addon()` built `Config(...)` **without reading** `broadlink_ip` / `ir_code_oppo` / `ir_code_kodi`, so `ir.configured()` was **permanently False** even when the user filled in the UI. The fix was three setting reads — and the reliability tunables were deliberately kept as module constants so there's never a `settings.xml` id without a matching dataclass field, closing that silent-drop class of bug for good.

### Act IV — the pure-CEC experiment (`CEC-Control-Experiment`, `service.oppokodibridge.cec`)

Despite the IR path being complete and tested, the operator **forked v3 and stripped IR entirely** (`c2144f6`, PR1), committing to spec-legitimate HDMI-CEC with zero extra hardware. A new add-on id (`service.oppokodibridge.cec`) lets it install **beside v2 and v3 for direct A/B/C comparison**. The thesis, stated as a design constraint: CEC has no "give-back" primitive and only two routing messages — `<Active Source>` (a device announces *its own* source) and `<Set Stream Path>` (**TV-only**; libCEC enforces "only the TV is allowed to send `CEC_OPCODE_SET_STREAM_PATH`"). So no third party may legitimately drive the TV to the OPPO's input. The only lever is each device's own One-Touch-Play, and the accepted price is the OPPO power-cycle (~20–24s per handoff). A 2-button **desktop CEC Switcher** (tkinter → PyInstaller exe) and the one-shot **`script.cecreclaim`** Kodi helper let the TV be switched both ways without the PC ever being on the CEC bus.

The load-bearing invariant of this whole act is **NEVER RE-ASSERT**:

- Each TV-input assertion is **single-shot** and tied to an event (OPPO grabs once on play, Kodi reclaims once on stop, in a `finally`). There is **no standing monitor** re-asserting active source. CEC is open-loop and can't distinguish "the TV missed my frame" from "the user switched away," so a re-asserter would override a manual input change and make the TV **un-leaveable**. Trading retry reliability buys back the user's ability to switch inputs manually and have it stick.
- A persistent reclaim flag could fire `CECActivateSource` at **BOOT** (a flag surviving a sub-second power-down window) — fixed by discarding the flag *once* at startup without firing (`733987d`).
- A clean modular rebuild (`87ee24f`, 0.3.0) ultimately deleted the flag mechanism entirely, moving the reclaim to a direct localhost JSON-RPC call and eliminating the whole stale-flag *class* of bug.

This line was hardened by **multiple adversarial bug-hunts**: a first hunt fixed 13 confirmed bugs (17 candidates, 4 refuted; `020581d`, 0.4.0), a second fixed 9 more and made the stop-watcher tri-state so a network blip can't yank the TV mid-playback (`3319dfd`, 0.4.1). When the multi-agent workflow was 529-blocked, the modules were swept by hand and still turned up two real v3-inherited bugs (`33c94b2`).

It also produced the **hardware-verified NFS finding** that explains years of frustration:

- **M9205 and M9207 need OPPOSITE NFS layouts.** M9205 mounts the file's *own folder* and plays the bare leaf name; the **M9207 Plus** (whose firmware misreports as UDP-203) mounts the export **root** and plays the full sub-path under `/mnt/nfs1` (`075cfef`, 0.4.3, verified live via `/getmovieplayinfo`). The add-on's M9205-only shape was *exactly* why it could never hand files to the UDP-203.
- **`#EJT`-as-grab was disproven.** A v0.4.3 assumption that `#EJT` grabs the TV was reversed by live testing (`aa026d6`, 0.4.4): on this clone `#EJT` ejects the disc tray, and in fact **no network command grabs the TV at all** — `#POF` sleeps, `#PON`/`#POW` only ACK, and CEC One-Touch-Play fires only on a full IR/remote power-on. `oppo_model` was demoted to selecting *only* the NFS layout; `power_cycle()` reverted to a plain `#POF → #PON` for every model. (The Kodi-side `script.cecreclaim` still works fine.)

### Act V — v3.1.0 convergence

The CEC-Control-Experiment work was re-IDed back to `service.oppokodibridge.v3` and **overwrote v3.0.0's Broadlink-IR switching** (`b4c4759`): `addon.xml` bumped 3.0.0 → 3.1.0, name "OppoKodiBridge v3 (playercorefactory)" → "OppoKodiBridge v3 (CEC)". `oppo_model` now defaults to **M9205** because that NFS layout lets disc-image `.iso` files loop-mount to `/mnt/iso` and play. (The news log also records an earlier hardware-disproven detour: `#EJT`-as-grab for the M9207 was wrong — only a real IR/remote power-on fires One-Touch-Play.) 73 off-box tests pass.

When folded into this repo (`bfa7753`, see [`CONSOLIDATION_NOTES.md`](./CONSOLIDATION_NOTES.md)), the v3 working tree keeps the **current pure-CEC files** (`cec.py`, `service_cec.py`, `detector.py`, `monitor.py`, `orchestrator.py`) and re-adds a **v3.0.0 IR stub** `ir.py` (a 38-line "stubbed until the RM4 is in hand / not yet implemented" placeholder) plus `service_v3.py`. The **complete IR path** — the hand-rolled `broadlink_rm4.py` and the real ~94-line `ir.py` sequencing layer — is **not** in the working tree; it survives only via git history on the `OppoKodiBridge-v3/ir-blaster-integration` and `OppoKodiBridge-v3/main` branches (which `CONSOLIDATION_NOTES.md` points to). So no information is lost, but only once you include those branches, not the working tree alone. `addon.xml` ships the pure-CEC service (`service_cec.py`) as the entry point.

### Act VI — the productized line: `script.oppo203.iso.external` + Windows configurator (2.9.17)

The largest and original lineage (510 commits) is the mature, productized one: a Kodi add-on that detects eligible disc-style media and hands it to an external OPPO-class player (keeping loose files internal), paired with a **Tauri 2 / React Windows configurator**, and held to an unusually high engineering bar.

- **MVP-first restart (2.0.0):** rather than attempt the full historical superset merge, it restarted from the reconstructed v1.x baseline as an External-Player MVP. It nailed the core invariant: stock OPPO UDP-203/205 preserve `#PON`/`#POW` exactly, and only Chinoppo-style clones rewrite wake to `#EJT` — plus the rule that a clean TCP close is **not** a playback stop (only explicit `@UPL`/`@UPW` events are).
- **The coverage-gate saga (2.9.13):** the enforced coverage floor was ratcheted 85 → 99, briefly lowered to absorb a Black reformat, then **dropped 98 → 50** under a "realistic Kodi testing strategy" (`409acc0`) that omitted UI/glue — only to be **restored to 99% the very next day** (`423e5b2`) on the finding that coverage never actually dropped, only the *policy* did; the omitted modules were already 94–100% covered. A pre-push hook now enforces 99% locally (`ecdb54d`).
- **Property/fuzz testing found crashes hand-written tests missed:** a Hypothesis-or-deterministic-fallback suite immediately found three real production bugs — `i18n.L(float('inf'))` raising `OverflowError`, and `autoscript_helper.generate()` crashing on a non-numeric `telnet_port` (bare `int()`) and a non-string `mount_type` (`.lower()` before `str()`). A later pass (`c2a47a1`, #329) found the same root cause clustered in discovery's port parsing (`'8060/tcp'` / `inf` → `int(port or 23)` raises), fixed with a `_safe_port` helper. The README's lesson: *nobody writes `generate({'mount_type': 12345})` by hand.*
- **Disabled-by-default multi-vendor AVR framework (2.9.10):** Denon/Marantz (telnet `PWON`/`SI`), Onkyo/Integra/Pioneer (eISCP `:60128`, Pioneer experimental), Yamaha MusicCast, Sony (gated behind explicit acknowledgement, never logging PSKs) — each guarded, returning non-fatal `AvrResult` objects, never hooked into sequencing until Build 17, and every build's notes state `hardware_validation_claimed=false`. Build 16's AVR `http_handoff` eligibility fix shipped in the v2.9.16 release (`89976ee`).
- **The asymmetric 7th preset (2.9.15):** adopting the Xnoppo Elite V3 pure-HTTP/436 model added a **7th preset** that is an *asymmetric* matrix cell (`monitor_modes` gains `http` but only one preset row), giving 7 presets not 9 — a guard naively computing the routing × monitor Cartesian product would wrongly expect 9. The single source of truth is a 3-place contract (Python registries + `playback-presets.json` + configurator `presetsdb.ts`), pinned by two guards; pure-HTTP became the default for new installs while the six prior presets stayed byte-identical.
- **`installer/` → `configurator/` rename:** the Windows companion app was scaffolded as `installer/` but renamed wholesale once the install-vs-configure distinction was settled (`7815818`): Kodi *installs* the add-on; this app only *configures* it. The rename swept the directory, product name ("OppoKodiAddon Configurator"), the npm/Cargo package (`oppokodiaddon-configurator`), and the Tauri bundle id.
- **The configurator honesty pivot (v0.9.10):** a cluster of fixes ripped out **fabricated UI results** — a hardcoded `10.0.1.42` with a faked OpenSSH fingerprint, a dead "Find on network" control, and a Step 4 TV-mute test faking success with a `setTimeout` and a fabricated "command transmitted 124 ms" (hardcoded `10.0.1.51`) — and wired in **real** `ping_host`/`ssh_test`/`smb_test_write`/`scan_kodi_hosts`/Roku-ECP-or-ADB probes (`2e560d4`, `491750a`, `b26e919`; #353–#355). "Never show a result you didn't actually obtain" became the configurator's defining discipline. The companion `:436` console was also fixed (`4944af4`) to run the real `emby-chinoppo-bridge` handshake (UDP `NOTIFY OREMOTE LOGIN` to `:7624`, then `GET /signin?{appIconType,appIpAddress}`) instead of a wrong `0x55` broadcast and a wrong `{user,password}` body.
- **Operator override — "`#EJT` is only for the M9702-Plus" (2.9.17):** a hardware-validated correction flipping the **whole M9205 family** to `#PON` wake (`dec1e6c`, `8858693`) because on validated M9205 hardware network power drives CEC active source. This needed a startup guard (`27aac59`) so an opt-in `kodi_startup_power_on` doesn't yank the TV to the player at boot — and forced the configurator's "Wake & confirm" wizard to send the *per-model* wake from a single source of truth (`playersdb.modelWakeCommand`, `e4b0830`) instead of a brand-level `isClone ? #EJT : #PON` heuristic. A configurable `oppo_disc_folders` route was first built across both the add-on and the configurator, then **scoped to the add-on only** (`27242c4` → `bd4c51e`).
- **The honest-signature discipline (sustained):** every release summary, README, and `HARDWARE_VALIDATION.md` states "Software-verified release. Hardware validation not performed / not claimed," and refuses to mark any device path hardware-validated without a real tester report. CI was also flipped local-first — the credit-consuming `claude-review` workflow disabled, gates run locally, and `*.sh` pinned to LF so a CRLF checkout doesn't break the WSL bash packaging (`1c970e5`, `c19900a`, `2838f17`).

---

## Add-on inventory (current state)

| Add-on id | Version | Lineage / role |
|---|---|---|
| `script.oppo203.iso.external` | 2.9.17 | Productized external-player line + Windows configurator (configurator 0.9.15); 510 commits |
| `service.oppokodibridge` | 2.0.14 | v2 HTTP-handoff bridge; the CEC-bus wars; 36 commits |
| `service.oppokodibridge.v3` | 3.1.0 | Pure-CEC, no-blip playercorefactory line (was "playercorefactory", now "CEC"); 5 commits on its tip |
| `service.oppokodibridge.cec` | 0.4.5 | CEC-Control-Experiment add-on; fork-and-strip-IR; 13 commits |
| `script.cecreclaim` | 0.1.0 | One-shot Kodi helper: `CECActivateSource` reclaim target |

---

## How this repo was assembled

This is a real merge, not a flat copy. The repo was bootstrapped (`f90078d`: root `README`/`.gitignore`/`.gitattributes`), then each source repo was run through **`git filter-repo --to-subdirectory-filter`** so every original commit is preserved with its files already namespaced under its subdirectory — and `git log` / `git blame` work across the full timeline.

- Three sources were merged in as subtrees via three **two-parent merge commits**: `2406a78` (`script.oppo203.iso.external/`), `242612d` (`OppoKodiBridge/`), `1c17db0` (`OppoKodiBridge-v3/`).
- A **fourth** project, `CEC-Control-Experiment/`, was folded in **later** on branch `consolidate/fold-cec-and-v3.1.0` (`4525b93`, parents `bd4c51e` + `9568941`) with its full 13-commit history. (The root README originally documented only three; the fourth arrived via this branch and `CONSOLIDATION_NOTES.md`.)
- **Every source branch is preserved** as `<subdir>/<branch>` and is an ancestor of one consolidated `main` — e.g. `script.oppo203.iso.external/release/v2.9.13`, `OppoKodiBridge-v3/ir-blaster-integration`, `OppoKodiBridge/main`, `CEC-Control-Experiment/main`, plus ~16 `script.oppo203.iso.external/claude/*` and `chore/*` working branches (`7708b96` documents the convention).
- History is intact across the merge: commits *touching each subdirectory* on the consolidated line are `script.oppo203.iso.external` = 510, `OppoKodiBridge` = 36, `OppoKodiBridge-v3` = 5, `CEC-Control-Experiment` = 13. The consolidation branch totals **740** commits once the merge commits and every preserved `<subdir>/<branch>` are counted (the per-subdir figures are not meant to sum to it).
- Built release `.zip` artifacts were **deliberately not** carried over (reproducible, gitignored build output, available on each repo's GitHub Releases); the original standalone working folders were moved to a sibling `_archive/` rather than deleted.

See **[`CONSOLIDATION_NOTES.md`](./CONSOLIDATION_NOTES.md)** for the full union/branch map. An earlier private placeholder, `skull-01/Oppo-Repo`, was empty and is **superseded by this repo** as the real consolidated home.

---

## Honest status

Treat the whole tree as **software-verified only** unless a milestone says otherwise. Test suites are extensive (16 / 73 / 83 off-box tests across the lineages; a 99% coverage gate on the productized line), every release follows an "honest-signature" discipline that **refuses to claim hardware validation without a real tester report**, and the documents track exactly what was verified in-session (`tsc`/`vitest`/build, `pytest`/`ruff`/`mypy`/coverage, mocked network, browser-rendered UI) versus what was not (live `:436` mount/play/confirm, ISO auto-heal, HDMI/CEC timing).

The handful of claims that *are* hardware-verified on the operator's real devices are tagged as such above and in the source docs: the **M9205 `#PON`** wake behavior, the **M9205 vs M9207-Plus NFS layouts**, and the **disproven `#EJT`-as-grab** finding (no network command grabs the TV on this clone). The CEC switch on `service.oppokodibridge.v3` / `service.oppokodibridge.cec` is software-verified; live CEC hardware validation remains pending.
