# CONFIGURATOR HANDOFF — read me first

> **Claude Code: this file is your entry point.** Read it fully, then follow "What to do"
> at the bottom. A companion archive **`configurator-handoff.zip`** ships alongside this
> file — unpack it (see step 1) for the full design spec and a clickable prototype.

---

## 1. What ships with this file

- **`CONFIGURATOR_HANDOFF.md`** — this file. Self-contained: overview + the full wiring
  contract. You can understand the task from this alone.
- **`configurator-handoff.zip`** — supporting material. Unzip into `docs/configurator/`:
  ```
  docs/configurator/
    design/README.md            full implementation handoff (all 23 screens, tokens, state)
    design/FIGMA_HANDOFF.md      Figma rebuild guide (only if enriching UI in Figma)
    design/source_design_doc.md  original product spec
    design/prototype/            working clickable reference — open the .html in a browser
  ```
  Suggested commit layout: keep this file at `docs/configurator/CONFIGURATOR_HANDOFF.md`
  and the unzipped contents beside it.

---

## 2. What this is

The **OPPO Installer Wizard** is a **Windows configurator** — a guided setup app that runs
on the user's PC, reaches the Kodi box over the network, writes this add-on's settings, and
deploys the two generated files (`playercorefactory.xml` + the remote-bridge keymap) into
Kodi `userdata/`.

**This add-on already anticipates it.** In `resources/lib/kodi/installer.py`:
- `NETWORK_SETTINGS_MANAGED_NOTE` — *"These connection values are normally set by the
  configurator on your PC."*
- `network_settings_menu()` shows fields as *"Managed by the configurator"* and a read-only
  *"Kodi box address: set on your PC (configurator)"*.

The wizard **is** that configurator. This handoff is the contract between them.

**In scope:** writing `settings.xml` IDs + deploying the two generated files.
**Out of scope:** OPPO/TV/AVR control logic — it already lives in `resources/lib/`. The
configurator drives the **existing** generators and writes **existing** setting IDs; it does
not reimplement protocols.

---

## 3. Existing generators to drive (do NOT reimplement)

All in `resources/lib/kodi/installer.py`:

| Generator | Produces | Triggered by (wizard step) |
|---|---|---|
| `build_playercorefactory_file_xml()` / `write_playercorefactory_file()` | ready-to-copy `playercorefactory.xml` (uses `python_path` + 4K tag rule `XML_4K_TAG_FILENAME_PATTERN`) | Step 1 install + Playback Test |
| `build_keymap_file_xml()` / `write_keymap_file()` | remote-bridge keymap (`userdata/keymaps/oppo203iso.xml`) | Step 1 install |
| `generate_transfer_files(...)` | both, returns `{kind: path}` | Step 1 "Generate & save files" (Tier C) |
| `run_oppo_discovery()` → `oppo.oppo_control.discover_oppo(timeout=5.0)` | multicast discovery, auto-applies `oppo_ip` | Step 2 "Find on network" |
| `show_tcl_presets()` (`TCL_ADB_PRESETS`) | writes `oppo_input_adb_shell` + `kodi_input_adb_shell` | Step 4 HDMI (ADB/TCL) |
| `show_architecture_choice_dialog()` | sets `playback_architecture` + `architecture_choice_made` | Step 1 (wizard assumes `external_player`) |

The wizard's install **tiers** are just *how* the two generated files reach `userdata/`:

| Tier | Mechanism | Restart Kodi |
|---|---|---|
| A — auto-write + auto-apply | SFTP into `userdata/` over SSH, then `systemctl restart kodi` | configurator |
| B — auto-write (SMB) | copy into the `userdata` SMB share | user |
| C — manual | `generate_transfer_files()`, user copies the `generated/` folder | user |

SSH (Tier A) is only used during setup — it is safe for the user to disable it afterward;
the handoff itself never uses SSH.

---

## 4. Screen → setting map (verbatim IDs from `resources/settings.xml`)

Enum values listed in declaration order (index 0 first). Kodi may persist an enum as its
value string *or* its zero-based index; `settings_reader` / `installer._resolve_enum()`
normalize both.

### Step 0 — Playback chain setup (prereq gate)
No settings. Conceptual gate (player must already reach media via SMB1/NFS/USB).

### Step 1 — Kodi box
| Wizard field | Setting ID / symbol | Notes |
|---|---|---|
| Kodi box IP | *(no add-on setting)* | Configurator's target address; held configurator-side. Shown read-only in-add-on. |
| python path (implicit) | `python_path` (default `/usr/bin/python3`) | Baked into generated `playercorefactory.xml` `<args>`. |
| Tier A SSH creds | *(configurator-side only)* | Never written to add-on settings. |
| Architecture | `playback_architecture` = `external_player` | Wizard assumes external_player; `service_interception` is the alternate. |

### Step 2 — Player (OPPO / clone)
| Wizard field | Setting ID | Values / notes |
|---|---|---|
| Brand → model | `oppo_hardware_model` (enum) | Maps 1:1. Order: `udp_203, udp_205, chinoppo_m9201, chinoppo_m9203, chinoppo_m9205c, chinoppo_m9702, ipuk_uhd8592, giec_bdp_g5300, magnetar_udp800, reavon_ubrx100, reavon_ubrx110, reavon_ubrx200, chinoppo_m9200, chinoppo_m9205, cineultra_v203, cineultra_v204, magnetar_udp900`. |
| Player IP | `oppo_ip` (default `192.168.1.50`) | |
| Port (23) | `oppo_port` (default `23`) | IP control. |
| WoL (optional) | `oppo_use_wol`, `oppo_mac`, `oppo_wol_broadcast` | Best-effort wake. |
| Wake/stop behavior | `oppo_start_commands` (`#PON\n#PLA`), `oppo_stop_commands` (`#STP`), `oppo_already_on_mode` | The `#EJT` eject-to-wake rewrite for clones is applied at send-time inside `oppo.oppo_control` from `oppo_hardware_model` — the wizard does **not** write `#EJT`. |
| warning-only brands | `oppo.hardware_validation_readiness` / `hardware_capabilities` | Magnetar / Reavon stay warning-only. |
| Discovery | `run_oppo_discovery()` | auto-applies `oppo_ip`. |
| Wake & confirm test | `oppo.oppo_control` over `oppo_port` | `#QPW` status query + `#PON`/`#EJT`. |

### Step 3 — TV
| Wizard field | Setting ID | Values / notes |
|---|---|---|
| Backend | `tv_backend` (enum) | `adb, sony_bravia, lg_command, samsung_command, custom_command, roku_ecp, smartthings`. Derived from brand/platform. |
| TV switching on/off | `tv_switching_enabled` (default true) | false on "drop to manual switching". |
| TV IP | `tv_ip` (default `192.168.1.60`) | |
| ADB | `tv_adb_port` (5555), `adb_path`, `adb_connect_before_switch` | adb backend. |
| Sony PSK | `sony_psk` | sony_bravia; never logged. |
| Roku ECP port | `roku_ecp_port` (8060) | roku_ecp. |
| SmartThings | `smartthings_token`, `smartthings_device_id`, `smartthings_experimental_acknowledged` | smartthings; experimental gate. |
| Control test (mute) | `tv.adb_control` / `tv.roku_ecp_control` / `tv.tv_control` | "input-finding deferred" = wizard's `tvAdbWeak` flag. |

### Step 4 — HDMI Input capture (field depends on active `tv_backend`)
| Backend | OPPO-input setting | Kodi-input setting |
|---|---|---|
| adb | `oppo_input_adb_shell` | `kodi_input_adb_shell` |
| roku_ecp | `roku_oppo_key` (`InputHDMI1`) | `roku_kodi_key` (`InputHDMI2`) |
| sony_bravia | `sony_oppo_hdmi_port` (int) | `sony_kodi_hdmi_port` (int) |
| lg_command | `lg_oppo_command` | `lg_kodi_command` |
| samsung_command | `samsung_oppo_command` (`{tv_ip}`) | `samsung_kodi_command` |
| custom_command | `custom_oppo_command` | `custom_kodi_command` |
| smartthings | `smartthings_oppo_input_id` | `smartthings_kodi_input_id` |

- Ask-first → writes the chosen HDMI number into the backend field (ADB/TCL via
  `show_tcl_presets()` / `TCL_ADB_PRESETS`; stored preset id in `tv_adb_preset`).
- ADB-weak funnel: HDMI number → CEC One-Touch-Play → blind-cycle → manual
  (`tv_switching_enabled=false`).

### Final — Playback Test
| Element | Symbol |
|---|---|
| Disc eligibility | `kodi.disc_classification.XML_4K_TAG_FILENAME_PATTERN` + `include_disc_folder_rules` |
| Routing file | `build_playercorefactory_file_xml()` |
| Return-on-exit | `switch_back_on_exit` (default true) |

---

## 5. Leave at defaults / out of scope

All `avr_*`; `reconnect_*`; `hold_mode` + pollers; `trickplay_suppress_seconds`;
`oppo_http_*`; `oppo_experimental_filelist_enabled`; `oppo_jailbreak_enabled`;
`oppo_autoscript_shell_handler`; `addon_language`.

---

## 6. Repo ground rules (from AGENTS.md / CONTRIBUTING.md)

- Branch + PR to `main`; **never commit to `main`**.
- Don't weaken the **"software-verified / hardware validation not claimed"** wording.
- Narrow, test-backed slices; finish each change with one copy-paste test command.
- Runtime ZIP allowlist excludes `docs/` — this handoff is dev-only, never shipped in the
  installable add-on.

---

## 7. Open questions — confirm against source BEFORE coding

1. **`playback_architecture` / `architecture_choice_made`** are read in `installer.py` but
   are not in the `settings.xml` snapshot used for this doc — confirm they exist (hidden
   setting?) or are written programmatically.
2. **Write transport** — does the configurator write Kodi's `settings.xml` / `addon_data`
   over SFTP/SMB directly, or via an add-on endpoint? `network_settings_menu()` implies
   direct file writes.
3. **`kodi_host`** appears in `installer._network_fields()` as an info row with no
   `settings.xml` entry — confirm where the Kodi box address is persisted configurator-side.

---

## What to do (Claude Code)

1. Unzip `configurator-handoff.zip` into `docs/configurator/` and skim `design/README.md`
   for the full 23-screen detail; open `design/prototype/OPPO Installer Wizard.html` if you
   want to see the intended UX.
2. **Do not write code yet.** First, verify §4's setting IDs and §3's generators against the
   actual source (`resources/settings.xml`, `resources/lib/kodi/installer.py`,
   `resources/lib/kodi/settings_reader.py`, `resources/lib/oppo/oppo_control.py`). Report any
   drift.
3. Answer the three §7 open questions from the code.
4. Propose a build plan (configurator stack + per-screen slices), then wait for the
   maintainer's go-ahead before implementing.
