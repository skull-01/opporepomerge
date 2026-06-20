# OPPO / Clone Installer App — Design Document

A Windows companion app for the `script.oppo203.iso.external` Kodi add-on. It sets up the
*handoff* — when a 4K UHD / Blu-ray disc image is launched in Kodi, Kodi tells the OPPO
UDP-203/205 (or a compatible clone) to take over playback, and the TV switches inputs to
match. The app does **not** set up how the player reaches media; that is a prerequisite.

This document has three sections:

1. **MVP** — the final agreed design we will build now.
2. **Roadmap** — deferred and out-of-scope items, for later versions.
3. **Discussion & rationale** — how each decision was reached, including the longer
   explanations and dead-ends that informed the design.

---

## Core concept: the playback chain

A **playback chain** is a named description of the user's full hardware topology plus how
the pieces are wired and addressed. It is the central object the app configures. Selecting
the hardware in each slot drives which presets, control backends, command quirks, and
generated files apply.

Slots in a chain:

- **Kodi box** — the device Kodi (and the add-on) runs on; a separate machine from the
  Windows PC running the installer.
- **TV / display** — gets its HDMI input switched on handoff.
- **External player** — the OPPO/clone that actually plays the disc image.
- **Media source** — where files live and how the player reaches them. *(Prerequisite
  only; not a configured node — see scope.)*
- **AVR** — *(out of scope.)*

A chain also captures **topology**, not just a parts list: which HDMI input each device
occupies, and the IP addresses involved.

Example chain (the maintainer's own): **CoreELEC on an Ugoos AM6B+** (Kodi box) →
**TCL Q9** (TV) → **Chinoppo M9205 V1** (player).

---

# 1. MVP — Final Design

The wizard runs in this order. Each step is described with its screens, branches, and the
decisions baked in.

## Cross-cutting principles

- **Software-verified posture.** A device's control method is a *software fact*; it is not
  a hardware-validation claim. The model database stores the resolved control method plus a
  separate `validated` flag that is true only when real per-device tester evidence exists.
- **Control failures are non-fatal.** TV (and AVR-style) control is optional. The core
  product — Kodi handing off to the player — works with zero TV automation. An unsupported
  or uncontrollable TV never ends the wizard; it lands on manual switching.
- **Merge, never blind-overwrite.** When writing files into Kodi, existing files are backed
  up and merged, never clobbered.
- **Honest tests.** Connectivity/control tests prefer a command the device *answers* (a
  query that returns a response) over a blind fire-and-hope command.

## Step 0 — Prerequisite gate

A confirm-to-continue screen establishing the scope boundary up front.

> **Before we start: your player must already reach your media**
>
> This wizard sets up the *handoff* — when you launch a 4K UHD / Blu-ray disc image in
> Kodi, it tells your OPPO/clone to take over, and switches your TV to match.
>
> It does **not** set up how your player reaches your files. Before continuing, confirm:
> you can already browse to an ISO on your OPPO/clone and play it directly, from the same
> media library Kodi uses.
>
> `[ I can already play ISOs on my player → Continue ]` `[ Not yet → Exit ]`

This is a **gate, not an advisory.** If the prerequisite is not met, every later step would
still "succeed" while playback fails silently at the end — the worst kind of bug to debug.

**Exit branch** (fail → don't dead-end the user):

> **No problem — let's get your player reading files first**
>
> Your OPPO/clone needs to reach your media on its own first. The player only speaks
> **SMB1**, so pick whichever fits:
>
> - **Local USB / hard drive on the player** — simplest; no network at all.
> - **Direct SMB1 share** — a Windows folder or NAS configured for SMB1/NTLMv1.
> - **NFS share** — often more reliable on OPPO than SMB1.
> - **SMB1 proxy** — bridge SMB1 through a dedicated Ubuntu VM, or re-share through Windows.
>
> Once you can browse to an ISO on the player and play it directly, come back.
>
> `[ Open setup guide ]` `[ Exit ]`

Bullets lead with **local USB** because it sidesteps the entire SMB1/network problem.
"Open setup guide" points to existing project material (Ubuntu-VM SMB1 proxy guide,
Windows/TrueNAS/NFS walkthroughs) — no new guide content required.

**Scope note carried forward:** file-*path* mapping (translating how Kodi vs. the OPPO
address the same file) stays out of scope here. HDMI-*input* mapping (Step 3.5) is in scope.
These are two different "mappings" and must not be conflated.

## Step 1 — Kodi box

Enter the Kodi box IP, then choose how setup files are installed and applied. Three tiers:

> **Your Kodi box**
> Kodi runs on a separate device from this app. Enter its IP so we can deliver your setup files.
> Kodi box IP: `[ __________ ]`
>
> How should we install — and apply — your setup files?
> - **Auto-write + auto-apply (SSH)** — we copy the files *and* restart Kodi for you.
>   Needs SSH enabled (default-on for CoreELEC/LibreELEC).
> - **Auto-write only (SMB)** — we copy the files; you restart Kodi yourself.
> - **I'll do it myself** — we generate the files; you place them and restart.

### Tier A — Auto-write + auto-apply (SSH / SFTP)

One login (password or key), one transport for both writing and restarting. SFTP-write +
SSH-restart on a single credential set — **not** SMB-write plus a separate SSH hop.

Checks (kept distinct so failures are diagnosable):
1. **SSH reachable** at `IP:22` — box answered, credentials accepted.
2. **userdata located & writable** — write a throwaway temp file via SFTP, confirm, delete it.
3. **Kodi restart available** — confirm the restart command can be issued (service/systemd on
   CoreELEC).

Then: "All set — we'll install your files and restart Kodi for you, backing up anything
already there."

*Scope:* Tier A's auto-restart is **CoreELEC/LibreELEC only** — the restart command is not
universal across platforms.

### Tier B — Auto-write only (SMB)

Checks:
1. **Box reachable** at the IP.
2. **userdata share accessible** (prompt for credentials if the share needs them).
3. **Write test passed** — temp file created + removed.

Then: "All set — we'll install your files with a backup. You'll restart Kodi yourself."

### Tier C — Manual

No connectivity. The app generates the files and shows where they go.

> **You'll install the files yourself**
> We'll generate `playercorefactory.xml` and the keymap and show you where they go.
>
> ⚠️ **Back up first.** Before copying anything in, make a copy of these from your Kodi
> userdata folder — if either already exists, our files will replace yours:
> - **`playercorefactory.xml`** — if you have one, it likely contains your other players.
>   Back it up or merge our entries by hand, or you'll lose them.
> - **`keymaps/` folder** — back up anything there you want to keep (risk is a same-name
>   collision, not the whole folder).
>
> If a file doesn't exist yet, there's nothing to back up — just drop ours in.

> **Where to put the files**
> Drop both files into your Kodi **userdata** folder (keymap goes in the `keymaps`
> subfolder). Usual locations:
>
> **CoreELEC / LibreELEC** — `/storage/.kodi/userdata/` → keymap `…/userdata/keymaps/`
> **Android** (Shield, Ugoos, etc.) — `/sdcard/Android/data/org.xbmc.kodi/files/.kodi/userdata/`
> → keymap `…/.kodi/userdata/keymaps/`  *(app-private storage may be hard to browse — use
> Kodi's file manager or an SMB/USB copy if you can't reach it)*
> **Windows** — `%APPDATA%\Kodi\userdata\` → keymap `%APPDATA%\Kodi\userdata\keymaps\`
> *(Linux desktop: you know where it is.)*
>
> 📌 **Remember this folder** — you'll need it again if you ever regenerate these files.
> After copying, **restart Kodi** so it loads the files.

*Tiers A/B common:* merge-not-overwrite with auto-backup of any existing
`playercorefactory.xml`; the write test always uses a throwaway file so a failed test never
leaves a broken config behind.

## Step 2 — TV (identification + control confirmation)

Identify the exact TV model, resolve its control backend, and confirm the app can control
the TV. **This step does not capture HDMI inputs and does not wake the OPPO** — that is
Step 3.5.

**Identification flow:** brand icons → exact model. Year (2018–2025) and size are
**find-my-model filters only** — they help the user locate their set; they do not determine
the control method (the smart-TV platform does).

**Control backends in play (all of them):**

| Backend | Reaches | Tier |
|---|---|---|
| `adb` | Google TV / Android TV (Sony current, TCL/Hisense Google variants, Philips, …) | probe-and-confirm |
| `roku_ecp` | Roku TVs (incl. TCL/Hisense Roku variants), HTTP :8060 | probe-and-confirm |
| `sony_bravia` | Sony Bravia IP control (pre-shared key) | probe-and-confirm |
| `smartthings` | Samsung via cloud API (token) | probe-and-confirm |
| `lg_command` | LG webOS via pre-paired external CLI command | bring-your-own-command |
| `samsung_command` | Samsung Tizen via pre-paired external command | bring-your-own-command |
| `custom_command` | Anything else (Panasonic, Vizio, projectors, CEC script) | bring-your-own-command |

CEC One-Touch-Play is **not** a coded backend; it is documented as a zero-config fallback
(the OPPO asserts active source on play and the TV follows).

"Supported" is **tiered**, not binary: probe-and-confirm backends vs. bring-your-own-command
backends. The result screen lands the user in the right tier rather than flashing a generic
green check.

**Model not found** (including all 2026+ TVs, which are deliberately outside the DB range):

> Enter TV IP → **[ Probe the TV (recommended) ]** or **[ Choose the method manually ]**

- **Probe** tests the ports the backends use (ADB :5555, Roku ECP :8060, Sony IP, …) and
  reports what answered. Honest path — it tests the real device on the real network.
- **Manual** drops to the backend picker, including the `custom_command` escape hatch.
- A failed probe ≠ unsupported — usually "debugging off" or "wrong IP." Route to fix +
  retry + manual, never to a dead stop.

**Enter TV IP** (required for nearly every backend regardless of branch).

**Basic control confirmation** — the only test in this step. Send an unambiguous command
that doesn't need inputs or the OPPO (power toggle, or a menu/mute blip), then:

> Did your TV react? `[ Yes ]` `[ No ]`

- **Yes** → "TV control confirmed."
- **No** → per-backend failure branch.

**The ADB funnel** (gate-then-expand):

- **Gate = the basic control test above.** If it passes, ADB control is confirmed and the
  enumeration/cycling complexity is never touched.
- **On fail, diagnose by cause:**
  - *Pairing not accepted / debugging off* → connection problem, not an input problem.
    Surface the **Allow-debugging** guidance (see below) and retry the gate.
  - *Connected but command did nothing* → genuine input-addressing weakness → **flag
    "input-finding deferred to Step 3.5."**

**ADB "Allow debugging" handling (ADB backend only):**

> **Heads-up: your TV may ask permission**
> The first time we connect, your TV (not this app) may show **"Allow USB debugging?"**
> Choose **Always allow from this computer**, then it won't ask again. If you don't see it,
> it may have appeared and closed — we'll retry.

- Gated to ADB only (Roku/Sony/etc. have no on-TV prompt).
- Pre-warn **before** the test fires, and lead the failure branch with it.
- Push the exact phrase **"Always allow from this computer"** (a one-time accept can drop on
  a TV reboot and break silently later).
- Handle the "no prompt at all" case: the dialog only appears if Developer Options →
  debugging is already on, so "no prompt" means debugging is off — guide to enable it.

## Step 3 — OPPO / clone player

Identify the player, get its IP, and confirm two-way IP control.

**Identification:** brand → model. ~17 presets from the add-on's existing registry; **no
year/size filters** (the list is small enough that a flat brand → model dropdown suffices).

- **OPPO** → UDP-203, UDP-205
- **Chinoppo** → M9201, M9203, M9205 (V1), M9205C, M9200, M9205, M9702
- **Magnetar** → UDP800, UDP900
- **Reavon** → UBR-X100, UBR-X110, UBR-X200
- **CineUltra** → V203, V204
- **iPUK** → UHD8592
- **Giec** → BDP-G5300

Model carries **posture**, not just a method: **Reavon = warning-only** (commands not
mutated); **Chinoppo / M9702 = wake-rewrite**. **"Other / clone"** lands on a conservative
default (stock `#PON`/`#PLA`) or an optional Chinoppo eject-to-wake preset — never a dead end.

**Player IP** — port 23 (IP control).

**Control test** — query-style: send a command the player *answers* (status/power query) to
prove two-way IP control, not a blind state-changing command.

**Clones — power on first; first test is wake & confirm:**

> **Power on your player first**
> Clones can be asleep and won't answer until woken. Make sure your player is plugged in and
> in **standby** (not switched off at the wall), then we'll wake it and confirm control.
> `[ Test: wake & confirm ]`

Send wake (`#EJT` for Chinoppo family) → **query the player and confirm it now reports
powered-on**. Success = "we sent wake → player responds as on" (this doubles as the IP-control
confirmation). Stock OPPO branches to `#PON` / plain query.

**Failure hints, cheapest-first:**

1. **IP Control isn't enabled** — Setup → Device Setup → IP Control / Network Control → On
   (wording varies by firmware). The #1 cause.
2. **Wrong IP / it changed** — confirm in the player's network settings; reserve it on DHCP.
3. **Not on the same network** — player + Kodi box + this PC must share the LAN/subnet (no
   guest WiFi / VLAN split). *(TV is irrelevant to this test — it had its own.)*

Clone-specific additions: player must be in **standby, not off at the wall** (network stack
must stay alive to receive the wake); **Quick Start** may need to be on so the player stays
reachable in standby.

## Step 3.5 — Input capture

Runs here, after the player step, because it needs the **OPPO awake** — which respects the
"no OPPO wake during TV setup" rule by construction. Captures **both** HDMI inputs:

- **The OPPO's input** (to switch *to* on handoff).
- **The Kodi box's input** (the **return target** for "switch back on exit").

**Capture method by backend:**

- **Addressable backends (Roku ECP, Sony):** ask-first → switch straight to it → confirm.
  Falls into a cycle only if the guess is wrong.

  > **Which HDMI input is your OPPO on?**
  > If you know, pick it and we'll confirm. If not, we'll find it for you.
  > `[ HDMI 1 ] [ HDMI 2 ] [ HDMI 3 ] [ HDMI 4 ]` `[ Not sure — find it for me ]`

- **Clean ADB** (passed the Step 2 gate): send discrete `KEYCODE_TV_INPUT_HDMI_n` + confirm.

- **ADB-weak** (flagged "connected but inert" in Step 2) → ordered fallback funnel, each rung
  with its own confirm, falling through on failure:
  1. **Ask the number** → send `KEYCODE_TV_INPUT_HDMI_n` → confirm. Stores a *real* HDMI number.
  2. **CEC One-Touch-Play** → wake OPPO so it asserts active source; TV follows. Stores
     "OPPO = CEC-asserted input" (no number needed to switch *to* it).
  3. **Blind-cycle** (last resort) → send input-advance key, "OPPO now? `[Yes][No,next][None]`."
     Human is the stopping condition. Stores the **lossy** record — "input after N advances,"
     not "HDMI n" — flagged internally as brittle if input order shifts.
  - "None / nothing works" → **manual switching** (user drives the TV with its own remote;
    the add-on simply doesn't switch). Never a dead stop.

**UX rules for all cycling:**
- Wake the OPPO first (`#EJT`/`#PLA`) so its input shows content, not a black screen that
  looks like an empty port.
- Warn before the first switch ("we're about to change your TV input").
- Always provide an exit from the loop.
- Return to the starting input when the step ends.

## Full Setup Test

Runs **last** — after Step 1 files are installed *and* Kodi has been restarted (the
remote-bridge keymap must be live for menu navigation to work).

Uses a **bundled, self-authored, genuinely playable UHD test ISO with a navigable menu**
(maintainer-produced; original content so it is legal to distribute and real enough that
"did it play" and "can you navigate the menu" are real tests). It must carry a
`4K`/`UHD`/`2160p` name tag and disc-style layout so Kodi's eligibility check routes it to
the player.

> **Full setup test**
> We'll copy a sample UHD disc into your library and play it end to end — confirming handoff,
> TV switch, playback, and Kodi-remote menu control.

> **Where should we put the test disc?**
> Save location: `[ browse / path ]`
> ⚠️ Must be on the media library **both Kodi and your player use** — not just a folder on
> this PC. If your library is a NAS or shared folder, point here to that share.
> After we copy it, **rescan your Kodi library** so the test file appears.
> `[ Copy test disc ]` → ✅ copied → `[ Run test ]`

Confirmation (yes/no each):

- Did the test disc start playing on your player?
- Did your TV switch to the player's input?
- Can you navigate the disc menu with your Kodi remote?

All yes → **setup verified, end to end.** Any no → branch to the relevant node:
- No play → player / routing (Step 3, playercorefactory).
- No switch → TV (Step 2 / Step 3.5).
- No menu control → keymap not loaded / Kodi not restarted (Step 1).

## TV model database (MVP scope)

- Range: **2018–2025**. 2026+ deliberately routes to the not-found probe/manual path.
- Stores the resolved **control method** (software fact) + a `validated` flag (true only with
  real tester evidence).
- **Maintained by the maintainer.** The installer **refreshes its copy from a public GitHub
  page** on demand.
- Year/size are find-filters; the control method derives from the platform.

---

# 2. Roadmap (future versions)

## Deferred to the next version (planned, not built yet)

- **AutoScript generation for Chinoppo clones.** An entire node, deferred. *Consequence for
  MVP:* the Tier C "remember this folder" line is worded as "if you ever regenerate these,"
  because in MVP `playercorefactory.xml` + keymap are the only files a manual user places. If
  AutoScript ships, that node will add further file handoffs and the "remember it" wording
  becomes a firm promise.

## Out of scope (not planned for now)

- **AVR node.** No AVR setup step in the wizard. AVR remains disabled-by-default in the
  add-on itself.
- **Media source as a configured chain node.** Media source stays the Step 0 prerequisite
  gate only; the app does not configure SMB1/NFS/proxy connections.
- **Auto-apply on non-CoreELEC platforms.** Tier A auto-restart targets CoreELEC/LibreELEC
  only. The JSON-RPC alternative restart path (telling Kodi's web interface to quit/reload)
  is noted but not adopted.
- **Probe write-back to the TV DB.** Successful probes of not-found TVs are used for that
  session only; they are not crowd-seeded back into the database (that would bump into the
  validation-claim line and create implicitly-trusted data).

## Parked (open, non-blocking — decide when built)

- **Step 3.5 / Tier A failure branches** — SSH-off, bad credentials, restart-not-supported
  detail screens not yet specified.
- **TV DB schema + GitHub refresh mechanics** — file format, hosting layout, how the app
  fetches/versions/caches the DB. Open sub-question retained from discussion: **per-model
  rows vs. per-lineup ruleset** (lineup rules + per-model exceptions is far less to maintain
  for the same brand → model → method UX). Maintainer owns this call.

---

# 3. Discussion & rationale

This section records how the design was reached, including the longer explanations that were
trimmed from the working conversation. Organized by decision.

## 3.1 The playback-chain concept

Introduced as the central data model so the wizard isn't a flat settings form but a
description of one hardware topology, from which presets/backends/files derive. Key
realization: a chain is **topology, not a parts list** — it must capture which HDMI input
each device occupies and the IPs, because TV input switching has nothing to act on
otherwise. The remote-bridge keymap target is *derived* from the chain, so it is not a
user-selected slot.

When the device-selection screen was first sketched (TV / Kodi box / player / AVR icons), the
biggest omission was the **media source** — the one mandatory node, while the *optional* AVR
had made the cut. The source also has variants that change everything downstream (NAS over
SMB1/NFS, a PC share, or local USB that removes the network problem entirely). The Windows PC
running the app is *sometimes* a chain node (when it's the SMB1 proxy) and sometimes just the
admin machine (as in the CoreELEC/TCL/M9205 example).

## 3.2 Why the media source is a gate, not a configured node

The add-on never moves bytes — it *triggers* the player, and Kodi and the player each resolve
the file independently. Getting media to the OPPO (which only speaks SMB1) is the single
hardest, most environment-specific part of these setups and dominated the source chat
history. Declaring it a prerequisite keeps the wizard focused on what it actually controls.

It is a **gate, not an advisory**, because without the prerequisite every later step still
reports success while playback fails silently at the very end — the most expensive failure to
diagnose. The exit branch leads with **local USB** because it removes the SMB1 problem
outright and users often don't realize it's an option; proxy routes go last because they're
heaviest. The framing "NFS is often more reliable on OPPO than SMB1" matches what the project
already told users, keeping it consistent.

**Two "mappings" kept separate:** the file-*path* translation (Kodi sees `nfs://…`, OPPO sees
`\\…` for the same file) stays out of scope; the HDMI-*input* mapping (Step 3.5) is in scope.
Conflating them would muddy later steps.

## 3.3 Step ordering: Kodi box first

Kodi-box identification was made the first real step (before TV). The "control confirmation"
framing was scrutinized and partly rejected: the Kodi box isn't a device you remote-control —
it's the host the add-on runs *inside*. So the real questions are **locate + reach +
characterize**, not "identify + control." The genuine, failable test is whether *the Windows
app* can reach the box to deploy files — which is exactly what `dev_build.py` already does.

## 3.4 Kodi-box delivery: SMB vs SSH, and the three tiers

- **SSH is not required to write files.** SMB writes them; this is the proven `dev_build.py`
  path and needs no SSH.
- **SSH's real value is *applying* the files** — `playercorefactory.xml` only loads at Kodi
  startup, so something must restart Kodi. SMB can't; SSH (or Kodi JSON-RPC) can. That's the
  one job SSH uniquely earns.
- **SSH can't be the only option** — it's off-by-default on stock Windows/Android boxes, so
  SSH-as-default would lock out exactly the platforms where SMB/manual is easier.

This produced **three tiers**: A (SSH/SFTP, write + auto-restart), B (SMB, write only), C
(manual). Tier A was deliberately wired as **SFTP-write + SSH-restart on one login**, not
SMB-write + a separate SSH hop, so it's one credential set, not two (SMB-share creds and SSH
creds are *different* auth and must not share a prompt).

**Tier A is CoreELEC/LibreELEC-only for auto-restart** because the restart command isn't
universal — on Windows/Linux-desktop Kodi it differs, and on Android there's no clean
SSH-restart at all. Adopting Tier A *was* the decision to support auto-apply; auto-apply on
other platforms was then explicitly put out of scope.

Manual (Tier C) must tell the user to back up **themselves**, naming files precisely:
`playercorefactory.xml` is the dangerous one (a single file Kodi reads — dropping ours in
replaces theirs and removes any other players they configured), whereas the keymap lives in
`keymaps/` where Kodi loads *all* files, so the risk there is a same-name collision, not
wiping the folder — hence "back up the `keymaps/` folder," not "the keymap file."

## 3.5 TV step: why exact-model identification, and the size/year reversal

Initial pushback: control method is a property of the **platform** (Google TV → ADB, Roku →
ECP, webOS → LG, Tizen → Samsung, Bravia → Sony), not the individual model, so size is pure
noise and year is a weak hint. A per-model DB also risks thousands of implicit
hardware-validation claims and goes stale instantly.

The maintainer chose **exact-model identification** anyway, for a cleaner user promise ("tell
me my model, I'll tell you yes/no and how"). That **reversed the size verdict**: with model
ID, size becomes a legitimate *find-my-model filter* (55Q9 vs 65Q9) — it still doesn't change
the method, but it helps locate the model. The validation-claim tension is reconciled by
storing the control method (software fact) separately from a `validated` flag.

An ADB-only scope was briefly considered and then dropped. The clarifying fact: **ADB works
on exactly one family — Android/Google TVs** — and even then needs debugging on, TCP :5555
reachable, RSA pairing accepted, and `adb` on the Kodi box. It reaches none of Roku/webOS/
Tizen. Keeping all backends gives: Sony two ways (adb or bravia-IP), Samsung two
(smartthings or command), LG one (command), TCL/Hisense split by OS (adb vs roku_ecp),
everything else via custom_command or CEC.

**The unsupported-TV branch was deliberately de-fanged.** Because TV control is optional and
non-fatal, an uncontrollable TV must land on "switch inputs with your remote, here's which
input" — never end the wizard. (A "squish gif" for unsupported TVs was floated; the right
target for drama, if any, is much rarer than "no ADB.")

## 3.6 TV control confirmation vs. input capture (the separation)

These were initially conflated and then correctly split:

- **Step 2 control confirmation** answers "can we control the TV at all?" — a backend-agnostic
  power/menu blip with a yes/no. It needs **no inputs and no OPPO**. Waking the OPPO here was
  explicitly rejected as belonging to the input step.
- **Input capture** (which HDMI the OPPO is on, plus the return target) needs the OPPO awake,
  so it moved to **Step 3.5**, after the player step. This also stopped "wake the OPPO" from
  being split across two nodes.

## 3.7 The ADB input problem (the hardest technical thread)

Whether ADB can enumerate and address HDMI inputs was examined closely. Conclusions:

- **No reliable enumeration.** There's no universal Android-TV API returning "this TV has 4
  HDMI ports"; you'd scrape per-OEM `dumpsys`/activities whose format differs by brand and
  firmware — works on the test device, returns garbage on the next. This is the per-model
  trap relocated into a parser.
- **No reliable addressing.** `KEYCODE_TV_INPUT` usually just opens the source menu rather
  than jumping to HDMI 3. Some OEMs expose `KEYCODE_TV_INPUT_HDMI_1..4` but support is
  inconsistent and unannounced. This matches the project's own "no universal ADB HDMI command
  is claimed."

So a true scan-and-cycle isn't dependable on ADB. The resolution adopted: **gate-then-expand.**
The basic ADB control test is the gate; only if it fails (and specifically in the
"connected-but-inert" case) does the input fallback open. The fallback is ordered by
reliability: **ask-the-number (real HDMI n) → CEC One-Touch-Play → blind-cycle (lossy
"input after N advances")** → else manual. Ask-first beats blind 4× cycling because in the
common case the user knows their input (one switch, not four), and "worst input last" is
avoided. Waking the OPPO before cycling is essential so its input shows content rather than a
black screen indistinguishable from an empty port.

For input-*addressable* backends (Roku ECP, Sony), genuine ask-first/auto-cycle works and is
reliable today.

## 3.8 Player step rationale

- **Identification resolves quirks, not a backend** (unlike the TV) — chiefly Chinoppo
  eject-to-wake (`#EJT`/`#PLA`) vs stock OPPO `#PON`/`#PLA`, plus Reavon warning-only posture.
  No year/size needed — ~17 models is a flat list.
- **Query-style control test** proves *two-way* IP control; a blind state-changing command
  proves only that you can transmit.
- **Clone wake-and-confirm as the first test** turns the clones' sleep quirk from a false
  failure into the actual verification. A non-responding clone may be **asleep**, not
  IP-control-off — so the failure path distinguishes standby-not-off and Quick Start, and the
  honest success condition is "sent wake → player now reports on."
- **Failure hints ordered cheapest-first** (enable IP Control → IP → same network), and the
  TV was dropped from this test's network hint because only the player + the test origin need
  to share the network here.

## 3.9 Full Setup Test rationale

The original idea — "play a fake ISO bundled in the installer" — can't work as literally
stated: a file on the Windows PC isn't reachable by the OPPO (the out-of-scope media-source
problem). Two genuinely different tests were separated:

- **(A) Routing/handoff** — needs only a path that *looks* eligible so the rules trip; doesn't
  need to truly play.
- **(B) End-to-end playback + menu nav** — needs a *real, playable* UHD ISO with a menu,
  already on the user's media source.

The maintainer chose **both, with the user picking**, and the installer **copies the test ISO
into the user's library** (turning a Windows-bound file into a reachable one). That copy is
itself a media-source write, so the destination must be on the shared library — hence the
explicit "must be accessible to both Kodi and OPPO" instruction and the library rescan. Final
decision: **bundled, self-authored, genuinely playable UHD ISO with menus**, so the full test
(play + remote menu nav) is real. This implicitly verifies the remote-bridge keymap landed —
so the test must run **after** Step 1 files are installed and Kodi restarted. The legal
blocker (commercial UHD discs are copy-protected and can't be bundled) is resolved by the
maintainer authoring original content.

## 3.10 Scope discipline

Several items were explicitly moved out of scope or deferred to keep the MVP shippable: AVR
node, media source as a configured node, auto-apply on non-CoreELEC platforms, and probe
write-back (all out of scope); AutoScript generation (deferred to next version). The TV DB
range was fixed at 2018–2025 with 2026+ handled by the not-found probe — a deliberate
boundary, not a coverage hole, precisely because the escape hatch already exists. The DB is
maintainer-owned and refreshed by the app from a public GitHub page.
