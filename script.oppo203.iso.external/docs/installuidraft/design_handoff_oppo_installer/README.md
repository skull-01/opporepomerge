# Handoff: OPPO Installer Wizard

A Windows companion app that walks users through setting up the [`script.oppo203.iso.external`](https://github.com/skull-01/script.oppo203.iso.external) Kodi add-on. The wizard configures the **handoff** — when a 4K UHD / Blu-ray disc image is launched in Kodi, Kodi tells the OPPO UDP-203/205 (or a clone) to take over playback, and the TV switches HDMI inputs to match.

This bundle is a **design handoff**, not a code drop. Read this README first.

---

## Contents

```
design_handoff_oppo_installer/
├── README.md                  ← you are here · Claude Code handoff
├── FIGMA_HANDOFF.md           ← Figma-specific setup guide
├── source_design_doc.md       ← the original product spec (read this for product context)
└── prototype/                 ← the HTML reference files
    ├── OPPO Installer Wizard.html
    ├── styles.css
    ├── shell.jsx              (window chrome, chain diagram, progress)
    ├── screens-1.jsx          (Step 0, 1, 2)
    ├── screens-2.jsx          (Step 3, 3.5, Test)
    ├── app.jsx                (router + tweaks)
    └── tweaks-panel.jsx       (design-time aesthetic toggle — strip in production)
```

To preview the prototype: open `prototype/OPPO Installer Wizard.html` in a modern browser. Use the Tweaks panel (top right) to flip between aesthetics, light/dark, and progress styles, and to jump directly to any of the 23 screens.

---

## About the design files

The files in `prototype/` are **design references created in HTML** — a clickable prototype showing intended look and behavior, not production code to ship. The task is to **recreate these designs in the target codebase's environment** using its established patterns.

The target environment is **a Windows desktop application** — the spec is explicit that this is a Windows companion app, separate from the Kodi box. Recommended stacks (pick what fits your skillset):

- **Tauri 2** (Rust core + web frontend) — the most natural port from this HTML prototype; small bundle size; native Windows feel.
- **Electron + React** — heavier but most familiar if you already know React; this prototype already uses React under the hood.
- **.NET 8 + WinUI 3 / WPF** — most "native Windows" feel; XAML-based; better for tight Windows integration. Higher rewrite cost from this prototype.

If you go Tauri or Electron, you can lift the React component structure from `screens-1.jsx` / `screens-2.jsx` more or less directly. The CSS system (`styles.css`) is framework-agnostic — usable in any of the three stacks with mechanical reformatting (CSS vars → XAML resources for WinUI/WPF).

---

## Fidelity

**High-fidelity.** Final colors, typography, spacing, interactions. Recreate pixel-perfectly using your target codebase's primitives.

The prototype ships **three aesthetic directions** as toggleable themes. **Pick one before implementation** — they're alternates, not coexisting. The default (Direction A) is the design's intended look unless the maintainer says otherwise.

| Direction | Vibe | Best for |
|---|---|---|
| **A — Warm Paper** | Things 3 / considered, generous whitespace, terracotta accent | Default. Lowers anxiety. Reads as "trustworthy, considered." |
| **B — Dim Lounge** | Craft + Sleeve, atmospheric, blurred surfaces, amber glow | Dark-default users; "evening home theater" mood. |
| **C — Living Room** | Flighty, friendly, sage + coral, slightly more playful | If you want delight + dimensional cards. |

---

## Product context (read first if unfamiliar)

The full product spec is in `source_design_doc.md`. The 90-second version:

- A **playback chain** has 4 nodes: **Media source** (prereq, not configured here) → **Kodi box** → **TV** → **Player**.
- The wizard configures the **handoff** between them, plus HDMI input switching.
- **6 wizard steps**: Step 0 (prerequisite gate), Step 1 (Kodi box), Step 2 (TV control), Step 3 (Player), Step 3.5 (Input capture), Full Setup Test.
- **TV/AVR control failures are non-fatal** — the user always lands on manual switching if control can't be established. Never dead-stop.
- **Tier system in Step 1**: A (SSH auto-write + auto-apply, CoreELEC/LibreELEC only), B (SMB auto-write), C (manual file generation).
- **ADB-weak fallback funnel in Step 3.5**: ask number → CEC One-Touch-Play → blind-cycle → manual.

---

## Screens / Views

There are **23 screens** total. They follow a wizard pattern with a persistent header (chain diagram + progress indicator) and a footer (back / continue buttons).

### Persistent shell

| Region | Description |
|---|---|
| **Title bar** | Windows 11 style. ~36 px tall. Left: app icon (gradient square) + "OPPO Installer · setup wizard". Right: min/max/close buttons (~46 px wide each, hover state, close goes red on hover). |
| **Header** | Padded 18 × 32 px. Top: progress indicator (3 styles, see below). Bottom: chain diagram. |
| **Content** | Scrollable, padded 28 × 40 px. |
| **Footer** | Back / Continue buttons. 14 × 32 px padding. |

### Progress indicator — 3 styles to support

1. **Stepper** (default) — horizontal row of `dot · label · separator` for each of 6 steps (0, 1, 2, 3, 3.5, Test). Dot shows step number, check when complete, accent fill when active.
2. **Sidebar** — 220 px left rail with named steps + dot indicators. Used as a layout shift (content takes remaining width).
3. **Minimal** — single line: `**Step name** · Step N of 6` + a thin progress bar (max-width 200 px).

### Chain diagram

Persistent topology view above the content. Four nodes laid out left-to-right with connectors:

`Media (gated) → Kodi box → TV ⇄ Player`

- Each node is `icon + label`. Icon is 36 × 36 px with 10 px radius.
- **Active node**: accent-filled icon, +5% scale, accent-soft glow ring.
- **Done node**: accent-soft background, accent-colored icon, small accent check badge bottom-right.
- **Gated node** (`media` after Step 0): muted color, dashed border, gray check badge.
- **Edges**: 32 px line. Animated gradient flow when current step is between two nodes. Bidirectional arrows (`⇄`) when Step 3.5 is active (TV ⇄ Player).

### The 23 screens

| # | Screen ID | Step | Purpose |
|---|---|---|---|
| 1 | `step0_gate` | 0 | Prerequisite gate. Confirm user can already play ISOs on player. |
| 2 | `step0_exit` | 0 | Media-source help branch (4 options: USB / SMB1 / NFS / SMB1 proxy). |
| 3 | `step1_intro` | 1 | Enter Kodi box IP + choose Tier A/B/C. |
| 4 | `step1_tierA` | 1 | SSH setup + diagnostic log (3 checks: reachable, userdata writable, restart available). |
| 5 | `step1_tierB` | 1 | SMB setup + diagnostic log (3 checks: reachable, share accessible, write test). |
| 6 | `step1_tierC` | 1 | Manual file generation. Backup warning + platform paths (CoreELEC/Android/Windows). |
| 7 | `step2_brand` | 2 | TV brand grid (Sony, Samsung, LG, TCL, Hisense, Roku, Vizio, Panasonic, Other). |
| 8 | `step2_model` | 2 | Model picker with year (2018-2025) + size filters + search + scrollable list. |
| 9 | `step2_notfound` | 2 | Model not found — choose probe (recommended) or manual backend pick. |
| 10 | `step2_probe` | 2 | Port probe diagnostic log (ADB, Roku, Sony, SmartThings). |
| 11 | `step2_adb_warn` | 2 | ADB allow-debug heads-up. Mock TV showing the on-screen prompt. |
| 12 | `step2_test` | 2 | Send mute test, ask "did your TV react?" yes/no. |
| 13 | `step2_fail` | 2 | Diagnose failure: pairing rejected / connected-but-inert / nothing-reached. |
| 14 | `step3_brand` | 3 | Player brand → model → IP. Posture callout (stock / wake-rewrite / warning-only). |
| 15 | `step3_test` | 3 | Wake-and-confirm diagnostic log. 4 checks. Mock player display LED. |
| 16 | `step3_fail` | 3 | 4 cheapest-first hints (IP control off / wrong IP / wrong subnet / standby vs off). |
| 17 | `step35_intro` | 3.5 | Input capture intro. Plan card + warning before TV input changes. |
| 18 | `step35_ask` | 3.5 | Ask-first HDMI tiles (1-4). 2 cycles: OPPO input, then Kodi box input. |
| 19 | `step35_fallback` | 3.5 | 4-rung ADB-weak fallback funnel. |
| 20 | `step35_done` | 3.5 | Inputs captured summary. |
| 21 | `test_setup` | Test | 2-option pick: bundled test disc OR user's own ISO. Both lead to test_confirm. |
| 22 | `test_confirm` | Test | 3 yes/no questions. Each "no" routes back to the owning step. |
| 23 | `test_success` | Test | Verified end-to-end. Summary of resolved chain. |

For pixel-level detail, see the JSX source files. Each screen function in `screens-1.jsx` / `screens-2.jsx` is a self-contained component.

---

## Interactions & behavior

### Navigation

- Each screen has a footer with **Back** and **Continue** (or contextual primary action).
- **Continue is gated** on the screen's success condition (e.g., test passed, model selected, copy completed).
- **Header progress indicator** allows jumping to any visited step (treat unvisited steps as locked or accessible based on your discretion — the prototype is permissive for design review).

### Diagnostic-log results (used in 6 screens)

The diag log is the central "honest test" UI. Anatomy:

- **Header**: status dot (gray pending / amber pulsing while running / green pass / red fail) + title + status text on right.
- **Rows**: icon (✓ pass / ✕ fail / ! warn / spinner running / dot pending) + label + monospace detail on right.
- **Footer**: plain-English summary in the success/fail color.
- Optional collapsible raw output pane below (monospace, 120 px max height).

### State transitions per screen (key examples)

**Step 1 Tier A (`step1_tierA`):**
- User enters SSH creds → clicks "Test connection".
- Diag log animates: each row goes pending → running → pass over ~1.5s.
- On all-pass: footer text becomes "All set — we'll install your files and restart Kodi for you", and `Continue to TV` button activates.
- On any-fail: footer goes red. Show inline retry + auth alternative (key vs password).

**Step 2 Test (`step2_test`):**
- Ready → click "Send test signal" → sending (1.5s) → sent (waits for user answer).
- TV mockup screen updates with each phase ("🔇 MUTE" → "check your TV").
- "Yes" → continue to Step 3 with `tvVerified: true`. "No" → `step2_fail`.

**Step 2 Fail (`step2_fail`):**
- 3 diagnose tiles. Each tile click sets specific state and routes:
  - "Pairing rejected" → retry the test
  - "Connected but inert" → sets `tvAdbWeak: true, tvVerified: true`, continue to Step 3
  - "Nothing reached" → sets `tvManualSwitch: true, tvVerified: true`, continue to Step 3

**Step 3 Test (`step3_test`):**
- Wake command is `#EJT` for clones, `#PON` for stock OPPO. Branch on `state.playerBrand`.
- Diag log animates: TCP reach → wake → query #QPW → confirm ON. ~2.2s total.
- Player mockup LED transitions: red standby → amber wake → green ON+READY.

**Step 3.5 Ask (`step35_ask`):**
- Two iterations: capture OPPO input, then Kodi box input.
- User picks an HDMI tile → TV mockup shows "switched to HDMI N" → "do you see {device}?".
- Yes confirms; advances to next iteration or `step35_done`.

**Test Setup (`test_setup`):**
- Two upfront tiles: "Use our test disc" / "Use one of your own files".
- Disc path: location picker → "Copy test disc" → diag log → "I rescanned and played it".
- Own path: 4-step numbered instruction card → "I played one — how did it go?".
- Both lead to `test_confirm`.

**Test Confirm (`test_confirm`):**
- 3 questions, yes/no each, with the "owning step" labeled on each.
- All yes → `test_success`. Any no → route to first failing step's main screen.

### Animations

- **Screen entry**: 0.25s ease, 6 px translateY + opacity 0→1.
- **Chain edge active**: animated gradient (`chain-flow` keyframe, 2s linear infinite).
- **Diag spinner**: 0.8s linear infinite rotate.
- **Pulse for running dots**: 1.4s ease in/out, opacity 1 → 0.5 → 1.
- **Button hover**: 0.15s ease; Direction C primary buttons lift 1 px on hover.
- **Tile hover**: 0.18s ease, +1 px lift, accent border, elevated shadow.

### Responsive

This is a **fixed-size desktop window**. Target a default 1180×820 with a soft min of ~1000×720. Don't bother below tablet sizes — it's a Windows desktop app.

---

## State management

Single flat state object per session. Key fields:

```ts
type WizardState = {
  // Step 0 — no state, just a gate
  // Step 1
  kodiIp: string;             // e.g. "10.0.1.42"
  tier: "A" | "B" | "C" | null;
  kodiVerified: boolean;
  // Step 2
  tvBrand: string | null;     // "sony" | "samsung" | ...
  tvModel: string | null;
  tvBackend: string | null;   // "adb" | "roku_ecp" | "sony_bravia" | "smartthings" | "lg_command" | "samsung_command" | "custom_command"
  tvVerified: boolean;
  tvAdbWeak: boolean;         // flagged from step2_fail "connected but inert"
  tvManualSwitch: boolean;    // flagged from step2_fail "nothing reached"
  // Step 3
  playerBrand: string | null; // "oppo" | "chinoppo" | "magnetar" | "reavon" | ...
  playerModel: string | null;
  playerIp: string;
  playerVerified: boolean;
  // Step 3.5
  oppoInput: number | "cec" | string | null;  // HDMI number, or "cec", or "cycle:N"
  kodiInput: number | string | null;
  // Test
  testMode: "disc" | "own" | null;
};
```

Persist to disk at every step transition so the user can resume after a crash or restart. The prototype keeps state in memory only.

### State transitions / chain completion

The chain diagram nodes light up based on these state flags:

| Chain node | Lit when |
|---|---|
| `media` (gated) | After Step 0 confirmed (always, going forward) |
| `kodi` | `kodiVerified === true` |
| `tv` | `tvVerified === true` (also true when `tvManualSwitch` or `tvAdbWeak` — we verified its state, just not as "fully controlled") |
| `player` | `playerVerified === true` |

### Side effects to wire up

These are the actual app behaviors the prototype mocks. The diag logs in the prototype are decorative — in the real app they reflect actual probes:

| Mock in prototype | Real behavior |
|---|---|
| Tier A SSH checks | SFTP connect via `ssh2-sftp-client` or equivalent; write/delete temp file; run `systemctl is-active kodi` |
| Tier B SMB checks | SMB ping; mount + write temp file |
| Tier C generate | Write `playercorefactory.xml` + keymap to a chosen local folder |
| Step 2 brand probe | TCP `connect()` to known ports per backend (ADB :5555, Roku :8060, Sony :20060, etc.) |
| Step 2 test signal | Send harmless command (mute toggle / `KEYCODE_VOLUME_MUTE` for ADB; `Lit_Mute` for Roku ECP; etc.) |
| Step 3 wake | `#EJT` for clones, `#PON` for stock; followed by `#QPW` query over TCP :23 |
| Step 3.5 input switch | `KEYCODE_TV_INPUT_HDMI_N` for ADB; ECP launch with HDMI input ID for Roku; etc. |
| Test setup disc copy | File copy to the chosen library path with progress feedback |

The add-on (the *Python* side, in the source repo) already has libraries for the OPPO/AVR/TV protocols — see `resources/lib/oppo_control.py`, `resources/lib/avr_*`, etc. The Windows installer doesn't need to reimplement OPPO control — it only needs to **set up the config files** the add-on consumes, plus run **connectivity probes** to give the user confidence.

---

## Design tokens

All tokens are defined as CSS variables in `prototype/styles.css`. There are 3 aesthetic directions × 2 modes (light/dark) = 6 token sets. **Pick one direction** before implementation; copy that direction's tokens into your app's design system.

### Direction A — Warm Paper (default — recommend this one)

**Light mode**
```
--desktop-bg     linear-gradient(135deg, #E7DCC9 0%, #D9C9AE 100%)
--window-bg      #FBF7EF
--titlebar-bg    #F4EEE3
--surface        #FFFFFF
--surface-2      #F6F1E8
--surface-sunken #F0EADD
--text           #29231D
--text-soft      #4E453C
--muted          #857B6E
--muted-2        #A89C8D
--border         #E7DDCB
--border-strong  #D6CAB4
--accent         #C2410C   (burnt orange)
--accent-hover   #9A3309
--accent-soft    #FBE8DA
--success        #4D7C0F
--success-soft   #ECF6D8
--warn           #B45309
--warn-soft      #FCEFCB
--danger         #B91C1C
--danger-soft    #FBE0E0
--info           #1D4E89
--info-soft      #DEEAF5
```

**Dark mode** — see `prototype/styles.css` `body.theme-a.mode-dark`.

### Direction B — Dim Lounge

See `body.theme-b.{mode-light,mode-dark}` in `prototype/styles.css`. Accent: amber `#F59E0B` (dark) / `#B45309` (light). Uses `backdrop-filter: blur(12-20px)` on cards and chain icons.

### Direction C — Living Room

See `body.theme-c.{mode-light,mode-dark}` in `prototype/styles.css`. Two accents: sage `#547755` (light) / `#8FAF8F` (dark), plus secondary coral `#C16A4C` / `#E5916F`. Primary buttons use a vertical gradient + bottom 2 px "lip" for friendliness.

### Typography

| Direction | Body / display | Mono |
|---|---|---|
| A | DM Sans (400, 500, 600, 700) | JetBrains Mono (400, 500, 600) |
| B | Space Grotesk (400, 500, 600, 700) | JetBrains Mono |
| C | Plus Jakarta Sans (400, 500, 600, 700) | JetBrains Mono |

Letter-spacing varies subtly per direction (`-0.005em` / `-0.012em` / `-0.014em`).

### Type scale

| Token | Size | Weight | Use |
|---|---|---|---|
| `.intro-title` | 30 px | 700 | Hero screen titles (Step 0 gate, Test success) |
| `h1.screen-title` | 26 px | 600 | Standard screen titles |
| `.screen-subtitle` | 15 px | 400 | One-line lede paragraph under title |
| `.tile-title`, `.intro-body` | 14.5–15.5 px | 600 / 400 | Cards / body |
| body / inputs | 13–14 px | 400 | Form labels, body |
| `.muted`, hints | 12–12.5 px | 400 | Hints, footer status |
| `.tile-badge`, `.sub-title` | 10.5–12 px uppercase | 600 | Eyebrows, badges |
| `.diag-detail`, `.kbd`, `.path` | 11.5–12.5 px | 400/500 mono | Diagnostic details, code |

### Radii

| Direction | Window | Card | Button | Input |
|---|---|---|---|---|
| A | 14 | 14 | 10 | 10 |
| B | 18 | 18 | 12 | 12 |
| C | 16 | 16 | 12 | 12 |

### Shadows

See `--shadow-window`, `--shadow-card`, `--shadow-elevated` in CSS. Direction B uses heavier shadows (atmospheric); Direction A uses single-layer soft shadows; Direction C uses dual-layer with a green tint in light mode.

### Spacing

The prototype doesn't define a formal scale — values are situational. As a rule of thumb:

- Inter-element gaps: 6 / 8 / 10 / 12 / 14 / 18 / 20 / 24 px.
- Card padding: 18-20 px (default), 14 px (compact path rows).
- Section/screen padding: 28-40 px.

---

## Components to extract

Build these as reusable components in your target codebase. Each lives in the prototype as a small JSX function — port the structure, don't copy the JSX literally.

| Component | Source location | Notes |
|---|---|---|
| `WinShell` | `shell.jsx` | Windows-chrome wrapper with title bar + content slot. |
| `AppHeader` (chain + progress) | `shell.jsx` | Chain diagram + chosen progress variant. |
| `Chain` | `shell.jsx` | Topology diagram; props: `active`, `completed`. |
| `Progress` | `shell.jsx` | Variants: stepper / minimal / sidebar. |
| `Sidebar` | `shell.jsx` | 220 px progress sidebar variant. |
| `Icon` | `shell.jsx` | Line-based 24×24 SVG icon set. 30+ icons; see source for names. |
| `DiagLog` | `screens-1.jsx` | Diagnostic-style result list with header dot, rows, footer message. |
| `FooterNav` | `screens-1.jsx` | Back / Continue button row. |
| Tile / Card / Callout / Chip | CSS classes in `styles.css` | Mostly CSS classes; trivial wrappers. |
| `HdmiTile` | `screens-2.jsx` (inline) | Big numbered HDMI 1-4 cards for input capture. |
| `BrandPill` | inline in screens | Brand-grid item with letter logo + name + hint. |
| `ModelRow` | `screens-1.jsx` | Row in the scrollable model list with backend chip. |
| `FallbackRung` | `screens-2.jsx` | Numbered rung in the ADB-weak fallback funnel. |
| `Question` | `screens-2.jsx` | Yes/No row in test_confirm. |
| `TvMockup` / `PlayerMockup` | CSS in `styles.css` | Decorative device illustrations. |

---

## Assets

- **No raster images, no external icons.** All icons are inline SVG in `shell.jsx` (`<Icon name="..."/>`). Replace with Lucide or Phosphor in your target codebase if preferred — the icon names map approximately to Lucide.
- **Fonts**: load via Google Fonts (already wired in `OPPO Installer Wizard.html`) or bundle locally for offline use (preferred for a desktop app):
  - DM Sans, Space Grotesk, Plus Jakarta Sans, JetBrains Mono.
- **App icon**: a simple gradient square with "O" letter (`titlebar-title-icon`). Replace with a real app icon before shipping.
- **Test ISO**: the wizard references `OPPO-Installer-Test-2160p.iso` (4.2 GB). This file does not exist in the bundle — it's the maintainer's job to author original content per the design doc (commercial UHD discs can't be redistributed). Ship it alongside the installer binary or download on first use.

---

## Implementation suggestions

1. **Start with the shell**. Get the Windows-style window, header, footer, and a placeholder content area rendering correctly. Pick one aesthetic direction and copy its tokens. Don't try to support multiple directions in production — pick one.
2. **Build the Chain and Progress components next**. They're persistent and reused everywhere. Get them right before screens.
3. **Build `DiagLog` next**. It's the second-most-reused component (appears in 6 screens). Make it animated, with rows that can transition pending → running → pass/fail over time.
4. **Then walk the screens in flow order** (Step 0 → 1 → 2 → 3 → 3.5 → Test). Each screen is small; most are <120 lines of JSX in the prototype.
5. **Wire side effects last**. Use the actual OPPO/SSH/SMB/ADB libraries; replace the mocked diag logs with real probe results streaming in.
6. **Persistence**: store the wizard state in `%APPDATA%/OPPOInstaller/state.json` (or equivalent on your OS layer). Restore on launch. Add a "Restart wizard" button.

---

## Out of scope for this design (deferred per spec)

- **AutoScript generation** for Chinoppo clones (planned for next version).
- **AVR setup** (out of scope; the add-on supports AVR but the wizard doesn't configure it).
- **Auto-apply on non-CoreELEC/LibreELEC** (out of scope; Tier A's restart command is platform-specific).
- **Probe write-back to the TV DB** (out of scope; probe results are session-local).
- **TV DB schema + GitHub refresh mechanics** (parked; not designed yet).

---

## Files

| File | Description |
|---|---|
| `prototype/OPPO Installer Wizard.html` | Entry HTML; loads fonts, React, Babel, and all JSX. |
| `prototype/styles.css` | Full design system: 3 aesthetics × light/dark via CSS vars. ~1400 lines. |
| `prototype/shell.jsx` | Windows chrome, chain diagram, progress indicators, icon set. |
| `prototype/screens-1.jsx` | Step 0, 1 (all tiers), 2 (all branches). |
| `prototype/screens-2.jsx` | Step 3, 3.5, Test. |
| `prototype/app.jsx` | Routing, state, tweaks-panel wiring. |
| `prototype/tweaks-panel.jsx` | Design-time aesthetic toggle. **Remove in production** — it's a design-review aid, not a feature. |
| `source_design_doc.md` | Original product spec from the maintainer. Authoritative for behavior. |
| `FIGMA_HANDOFF.md` | Sibling doc: how to set this up as a Figma file for further design work. |

---

## Questions to resolve before / during implementation

1. **Which aesthetic direction?** Pick one. Recommend A unless the maintainer says otherwise.
2. **Tauri / Electron / native Windows?** Affects how directly the prototype maps.
3. **State persistence path?** `%APPDATA%/OPPOInstaller/` is the obvious choice; confirm.
4. **What happens on Windows when the user closes mid-wizard?** Resume from same screen on next launch (recommended), or restart from Step 0? Spec doesn't say.
5. **Where do the generated `playercorefactory.xml` + keymap files come from?** The prototype assumes they're generated; in reality, the Python add-on already generates these into the add-on-data folder per its v2.9.12 release notes. The installer may need to call into the add-on's existing tooling, or have its own generator. Confirm with the maintainer.
