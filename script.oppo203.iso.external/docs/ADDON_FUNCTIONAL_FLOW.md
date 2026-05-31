# Add-on functional flow — how `script.oppo203.iso.external` actually works

**Scope:** the Kodi add-on (Python under `resources/lib/`, entry points `default.py` /
`service.py`). The Windows configurator is out of scope here.

**Signature:** code-verified against the current source at `main`@`900834b` (read, not run;
**no hardware validation**). Every box names a real function with a `file:line` anchor you
can click. Diagrams are [Mermaid](https://mermaid.js.org) — they render natively on GitHub
and in most Markdown previewers.

**The one thing to understand first:** this add-on does **not** stream video and never calls
Kodi's `setResolvedUrl`. "Playback" means **handing a physical OPPO Blu-ray player a disc to
play over the LAN** while Kodi just holds the playback slot open. Two architectures
(`playback_architecture` setting) both converge on the same pipeline in
[`external_player.py`](../resources/lib/kodi/external_player.py).

Jargon, once:
- **playercorefactory.xml** — a Kodi config file that tells Kodi "for files matching this
  rule, launch this external program instead of playing it yourself."
- **external player** — any non-Kodi program Kodi launches to handle a file; here it's our
  `external_player.py` wrapper.
- **keymap** — a Kodi config file binding remote/keyboard buttons to actions; ours forwards
  buttons to the OPPO.
- **sentinel** — a marker file (`oppo203iso-active`) whose mere existence means "a handoff
  session is in progress."
- **WOL / `#PON` / `#EJT` / `#QPL` / `#SVM`** — Wake-on-LAN, and OPPO IP-control commands
  (power on / eject-to-wake for clones / query-playback-status / set-verbose-mode).

---

## A. Architecture & entry points

`addon.xml` declares **two** Kodi extension points — a script (the menu + the remote-key
bridge) and a background service.

```mermaid
flowchart TB
    Kodi["Kodi — requires xbmc.python 3.0.0"]

    subgraph Manifest["addon.xml — two extension points"]
      direction TB
      Script["xbmc.python.script<br/>library = default.py<br/>(menu / executable)"]
      Service["xbmc.service<br/>library = service.py<br/>start = startup"]
    end

    Kodi --> Script
    Kodi --> Service

    Script -->|argv1 is oppo_key| Remote["oppo_remote.send_remote_key()<br/>oppo_remote.py:94"]
    Script -->|else| Installer["installer.main() — setup menu<br/>installer.py:919"]

    Service --> SvcMain["_service_main()<br/>service.py:455"]
    SvcMain --> StartupPwr["_kodi_startup_power_on() optional<br/>service.py:528"]
    SvcMain --> ArchBranch{"playback_architecture?"}
    ArchBranch -->|service_interception| IPlayer["InterceptionPlayer xbmc.Player<br/>service.py:236"]
    ArchBranch -->|external_player default| Heartbeat["idle heartbeat loop<br/>service.py:489"]

    Installer -. writes .-> Gen["addon_data/generated/<br/>playercorefactory.xml<br/>keymaps/oppo203iso.xml"]
    Gen -. user copies to .-> Userdata["Kodi userdata/"]
    Userdata --> PCF["Kodi playercorefactory engine"]

    Remote --> OppoCtl["oppo_control — TCP:23 / HTTP:436"]
    IPlayer --> Pipeline["external_player pipeline"]
    PCF --> Pipeline
```

**Anchors:** `addon.xml:6` (script), `addon.xml:9` (service, `start="startup"`),
`default.py:10-13` (argv dispatch).

---

## B. One-time setup (the installer menu)

The user opens the add-on once to choose an architecture and generate the two config files,
then copies them into Kodi's `userdata/`.

```mermaid
flowchart TD
    A["default.py → installer.main()<br/>installer.py:919"] --> B{architecture_choice_made?}
    B -->|no| C["show_architecture_choice_dialog()<br/>installer.py:505"]
    C --> D{user choice}
    D -->|External Player| E["set playback_architecture = external_player"]
    D -->|Service Interception| F["set playback_architecture = service_interception"]
    B -->|yes| M["setup menu — 14 actions<br/>installer.py:923"]
    E --> M
    F --> M

    M -->|Generate playercorefactory.xml| G["write_playercorefactory_file()<br/>installer.py:403"]
    M -->|Generate keymap| H["write_keymap_file()<br/>installer.py:425"]
    M -->|Discover OPPO| I["run_oppo_discovery()<br/>UDP multicast 239.255.255.251:7624<br/>installer.py:534"]
    M -->|Network settings| J["network_settings_menu()<br/>view/override TV / OPPO / AVR / Kodi IPs<br/>installer.py:835"]

    G --> K["generated/playercorefactory.xml<br/>player Oppo203ISO runs external_player.py<br/>rule routes tagged iso/bdmv/mpls"]
    H --> L["generated/keymaps/oppo203iso.xml<br/>FullscreenVideo buttons → RunScript oppo_key"]
    K --> N["user copies into Kodi userdata/"]
    L --> N
```

The generated `<player>` element (`installer.py:97`) is literally
`{python} "external_player.py" --addon-data "<dir>" --file "{1}"`, and the routing rule
(`installer.py:135`) is
`<rule filetypes="iso/bdmv/mpls" filename="<4K|UHD|2160p…>" player="Oppo203ISO"/>` with
`action="prepend"`. **XML mode is filename/path driven** — it cannot look inside an ISO, so
every rule requires an explicit `4K`/`UHD`/`2160p` tag in the name.

---

## C. Play-time — External Player mode (the spine)

This is the load-bearing path. Kodi's own playercorefactory engine matches the rule and
launches our wrapper as a subprocess; the wrapper orchestrates TV → AVR → OPPO, holds the
slot, then restores everything.

```mermaid
sequenceDiagram
    actor User
    participant Kodi as Kodi playercorefactory
    participant EP as external_player.main()
    participant TV as tv_control
    participant AVR as avr_sequence
    participant OPPO as oppo_control
    participant Player as OPPO or clone on LAN

    User->>Kodi: play "Movie 4K UHD.iso"
    Note over Kodi: rule matches filetypes iso/bdmv/mpls<br/>AND filename tag 4K|UHD|2160p
    Kodi->>EP: launch external_player.py --addon-data --file
    EP->>EP: read_settings()
    opt oppo_preflight_enabled
        EP->>OPPO: run_preflight() — QPW / QIS
        OPPO-->>EP: power / input / already_on
    end
    EP->>EP: mark_session_active() — write oppo203iso-active sentinel

    rect rgb(232,244,255)
    Note over EP,Player: fast_start() — order TV → AVR → OPPO, each non-fatal<br/>external_player.py:142
    EP->>TV: switch_to_oppo() — flip TV HDMI input
    EP->>AVR: pre_playback_sequence() — power_on? + select_input
    EP->>OPPO: run_start() — WOL, SVM verbose, then start commands
    OPPO->>Player: TCP:23 PON/EJT  OR  HTTP:436 /playnormalfile
    end

    rect rgb(245,236,255)
    Note over EP,Player: hold_playback() — occupy Kodi slot until player stops<br/>external_player.py:167
    loop until idle/stop or timeout
        EP->>Player: poll — QPL / HTTP getmovieplayinfo / verbose UPL push
        Player-->>EP: status
    end
    end

    rect rgb(232,255,238)
    Note over EP,Player: fast_return() — runs in finally:, even on error<br/>external_player.py:157
    EP->>OPPO: run_configured_commands("oppo_stop_commands")
    OPPO->>Player: stop commands TCP:23
    EP->>AVR: post_playback_sequence() — restore input
    EP->>TV: switch_to_kodi()
    EP->>EP: clear_session_active() — remove sentinel
    end
```

**Why the order matters:** `fast_start` switches the TV **before** waking the OPPO so the
input is ready when video appears; AVR sits between them. Each stage is **non-fatal by
design** (`_safe_tv_switch` at `external_player.py:121`, AVR warnings at `:152`/`:161`) — a
TV or AVR failure must never block OPPO startup or, more importantly, the `fast_return`
cleanup, which is why `fast_return` + `clear_session_active` live in a `finally:`
(`external_player.py:360-366`).

---

## D. Play-time — Service Interception mode

Same pipeline, different trigger. Instead of Kodi routing the file out via
playercorefactory, the service watches Kodi's own player, stops it, and threads into the
identical `fast_start → hold_playback → fast_return`.

```mermaid
sequenceDiagram
    actor User
    participant Kodi as Kodi Player
    participant IP as InterceptionPlayer
    participant Cls as intercept + disc_classification
    participant Run as _run_interception thread
    participant Pipe as external_player pipeline

    Note over IP: _service_main holds a live InterceptionPlayer ref<br/>(Kodi GCs unheld Player subclasses → silent callback loss)
    User->>Kodi: play a disc file
    Kodi->>IP: onAVStarted() Kodi 21+ / onPlayBackStarted() pre-21
    IP->>IP: _handle_started() → getPlayingFile()
    IP->>Cls: should_intercept_4k_disc_source(path)<br/>intercept.py:201
    Cls-->>IP: tagged 4K AND disc-style?
    alt not a tagged 4K disc-style source
        IP-->>Kodi: return — Kodi keeps playing (default)
    else sentinel already present
        IP-->>IP: skip (session active)
    else intercept
        IP->>Kodi: Player().stop()
        IP->>Run: spawn daemon thread
        Run->>Pipe: mark_session_active → fast_start → hold_playback
        Run->>Pipe: finally → fast_return → clear_session_active
    end
```

The intercept decision is `tag AND disc-style`: `has_uhd_disc_tag()`
(`disc_classification.py:51`, substring `4k`/`uhd`/`2160p`) **and** `is_4k_disc_style_source()`
(`disc_classification.py:80`, ISO or BDMV navigation/playlist — loose `.mkv`/`.mp4`/`.m2ts`
stay in Kodi).

---

## E. `hold_playback` — the 5-mode state machine

Once the OPPO is playing, the wrapper must keep the Kodi slot occupied until the disc stops.
`hold_mode` selects one of five stop-detection strategies (`external_player.py:167`).

```mermaid
stateDiagram-v2
    [*] --> Dispatch
    state "hold_playback(settings) — external_player.py:167" as Dispatch

    Dispatch --> HttpPoll: hold_mode = http_poll
    Dispatch --> QplPoll: hold_mode = tcp_qpl_poll
    Dispatch --> VerbosePush: hold_mode = verbose_push
    Dispatch --> ManualFile: hold_mode = manual_file
    Dispatch --> FixedTimeout: hold_mode = fixed_timeout, the default

    state "http_poll — GET getmovieplayinfo, idle x2 + trickplay suppress (:170)" as HttpPoll
    state "tcp_qpl_poll — QPL poll until idle x2 (:238)" as QplPoll
    state "verbose_push — persistent TCP, UPW/UPL push events (:269)" as VerbosePush
    state "manual_file — wait for stop file (:304)" as ManualFile
    state "fixed_timeout — sleep N min, default 180 (:315)" as FixedTimeout

    HttpPoll --> [*]: stop, idle, or timeout
    QplPoll --> [*]: idle or timeout
    VerbosePush --> [*]: stop event or timeout
    ManualFile --> [*]: stop file appears
    FixedTimeout --> [*]: timer elapsed

    VerbosePush --> FixedTimeout: connect FAILS — sets mode tcp_qpl_poll but that block is ABOVE, so control falls through to fixed_timeout — see Appendix BUG-1
```

The four active modes detect stop differently: HTTP poll reads `e_play_status` from
`/getmovieplayinfo` with a trick-play suppression window so fast-forward isn't mistaken for
stop; TCP QPL polls `#QPL`; verbose-push opens a persistent socket and listens for `@UPW 0`
/ `@UPL <stop>` push events; manual-file just waits for a sentinel file; fixed-timeout is a
blind sleep.

---

## F. OPPO control — start transports

`run_start` wakes the player, sets verbose mode, then sends the disc-start commands over one
of two transports chosen by `oppo_start_mode`.

```mermaid
flowchart TD
    A["run_start()<br/>oppo_control.py:611"] --> B["maybe_wake_on_lan() — UDP magic packet<br/>oppo_control.py:313"]
    B --> C["maybe_setup_verbose_mode() — SVM, non-critical<br/>oppo_control.py:180"]
    C --> D{oppo_start_mode}

    D -->|tcp_commands or tcp_then_http| E["run_configured_commands oppo_start_commands<br/>oppo_control.py:597"]
    E --> E1["_filter_commands_for_mode()<br/>drop PON if already_on<br/>oppo_control.py:552"]
    E1 --> E2["_resolve_hardware_wake_command()<br/>clone: PON → wake_command EJT<br/>oppo_control.py:579"]
    E2 --> E3["send_commands() → TCP:23<br/>oppo_control.py:70"]

    D -->|http_api or tcp_then_http| F["activate_http_api() — UDP 0x55 → port 436<br/>oppo_control.py:346"]
    F --> F1["signin_http_api() → /signin<br/>oppo_control.py:357"]
    F1 --> F2["play_media_http_api() → /playnormalfile<br/>oppo_control.py:432"]

    E3 --> Z["OPPO / clone plays the disc"]
    F2 --> Z
```

**Clone handling:** stock OPPO uses `#PON`; Chinoppo-style clones can't power on the same
way, so the wake command is rewritten to `#EJT` (eject-to-wake). Note this rewrite logic
exists in **three** places with different mechanisms — see Appendix.

---

## G. Remote-key bridge (control during playback)

While the disc plays, the TV shows the OPPO's HDMI input — but the remote events still reach
the Kodi box. The keymap forwards each button back through Kodi into our script, which
translates it to an OPPO command.

```mermaid
sequenceDiagram
    actor User
    participant Kodi as Kodi FullscreenVideo keymap
    participant Def as default.py
    participant Rem as oppo_remote.send_remote_key()
    participant Map as command_map 76 keys
    participant Player as OPPO player

    User->>Kodi: press a remote / keyboard button
    Kodi->>Def: RunScript(default.py, oppo_key, KEY)
    Def->>Rem: send_remote_key(KEY)
    Rem->>Rem: session active? (remote_bridge_only_when_active)
    Rem->>Map: look up normalized key
    Map-->>Rem: OPPO command
    alt power_on / power_toggle
        Rem->>Rem: resolve_power_on_token() — clone → EJT<br/>oppo_remote.py:216
    end
    alt cycle_audio / cycle_subtitle / seek_beginning
        Rem->>Player: HTTP getaudiomenulist / getsubtitlemenulist / setplaytime
        Note right of Rem: audio + subtitle fall back to TCP AUD / SUB on HTTP failure
    else normal key
        Rem->>Player: send_commands() → TCP:23
    end
```

The keymap is **static** — `_keymap_document_xml()` (`installer.py:204`) hard-codes every
`<FullscreenVideo>` binding; it is not regenerated from the 76-key command map.

---

## H. TV input switching

`switch_to_oppo()` / `switch_to_kodi()` dispatch to one of seven backends by `tv_backend`.

```mermaid
flowchart TD
    A["switch_to_oppo() / switch_to_kodi()<br/>tv_control.py:147 / :151"] --> B["_switch(settings, target)<br/>tv_control.py:88"]
    B --> C{tv_backend}
    C -->|adb| D["adb_control.switch_input()<br/>adb shell intent / keyevent<br/>adb_control.py:57"]
    C -->|roku_ecp| E["roku_ecp_control.switch_input()<br/>HTTP POST /keypress/InputHDMIx<br/>roku_ecp_control.py:99"]
    C -->|sony_bravia| F["_sony_set_hdmi() — JSON-RPC<br/>tv_control.py:54"]
    C -->|lg_command / samsung_command / custom_command| G["_run_external() — user shell command<br/>tv_control.py:34"]
    C -->|smartthings| H["smartthings_switch_input()<br/>HTTPS API, gated by ack flag<br/>smartthings_control.py:153"]

    classDef gated fill:#fff3cd,stroke:#cc9a06,color:#663c00
    class H gated
```

All seven backends are implemented. SmartThings (yellow) is **not** a no-op — it makes live
HTTPS calls but only after the user sets `smartthings_experimental_acknowledged`
(`smartthings_control.py:170`). TV switching is settings-gated and entirely optional
(`tv_switching_enabled`, `external_player.py:107`).

---

## I. AVR (receiver) sequencing

Optional audio-receiver power/input control, wrapped around the OPPO handoff. **Disabled by
default.**

```mermaid
flowchart TD
    A["pre_playback_sequence() / post_playback_sequence()<br/>avr_sequence.py:112 / :156"] --> B{"eligible?<br/>playback_architecture == external_player"}
    B -->|no| S1["skipped"]
    B -->|yes| C{avr_control_enabled?}
    C -->|false default| S2["skipped"]
    C -->|true| D["controller_factory() → validate_avr_settings()<br/>avr_control.py:200 / :123"]
    D --> E{avr_backend}
    E -->|denon_marantz| F1["Denon / Marantz — TCP:23"]
    E -->|yamaha_yxc| F2["Yamaha YXC — HTTP:80"]
    E -->|onkyo_eiscp / pioneer_eiscp| F3["Onkyo / Pioneer eISCP — TCP:60128"]
    E -->|sony_audio_api| F4["Sony Audio API — gated by ack"]
    F1 --> G["pre: power_on? + select_input<br/>post: restore_input if avr_restore_enabled"]
    F2 --> G
    F3 --> G
    F4 --> G
```

---

## Appendix — noticed while mapping (NOT fixed; flow doc is read-only)

These are correctness observations surfaced while tracing the real code. They are recorded
here for the operator, consistent with the §3c suspect-discipline; **no fix is made in this
doc**.

- **BUG-1 — `verbose_push` hold silently degrades to a 180-min blind timeout.** On TCP
  connect failure, `external_player.py:300-302` sets `mode = "tcp_qpl_poll"` intending to
  fall back to QPL polling, but the `tcp_qpl_poll` block is physically **above** (`:238`),
  so control falls through to the unconditional `fixed_timeout` default (`:315`). The
  comment at `:301` ("Fall through to tcp_qpl_poll logic below") is wrong about direction.
  Effect: a flaky verbose-push connection holds the Kodi slot for `fixed_timeout_minutes`
  (default 180) instead of polling for the real stop.
- **BUG-2 — diagnostics HTTP probe checks the wrong port.** `default.py:53-63` (`_http`
  helper in `run_diagnostics_dashboard`) connects to **port 80**, but the OPPO HTTP API is
  **port 436** (`oppo_control` HTTP path). The diagnostic reports HTTP reachability against
  a port the device doesn't serve.
- **Dead-at-runtime — `intercept.should_intercept()` whitelist/blacklist engine**
  (`intercept.py:243`) is tested but has no production caller; service interception uses
  `should_intercept_4k_disc_source` (`intercept.py:201`) instead.
- **Triplicated clone-wake logic.** The `#PON → #EJT` clone rewrite exists in three places
  with three different mechanisms: `oppo_control._resolve_hardware_wake_command` (`:579`,
  profile `is_clone`), `oppo_remote.resolve_power_on_token` (`:216`, profile `is_clone`),
  and `service._startup_wake_token` (`:603`, substring model markers). The three can drift.
- **AVR powers on but never off.** `pre_playback_sequence` can `power_on`, but no path ever
  powers the receiver off, and `avr_power_off_enabled` / `avr_volume_automation_enabled` are
  declared in settings yet have **no consumer** in any execution path.
