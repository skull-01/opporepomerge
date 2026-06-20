# Figma Handoff: OPPO Installer Wizard

How to set up a Figma file from this design so you can enrich it further visually. This doc is the **Figma-specific** companion to `README.md` — read that for product context, design tokens, and screen behavior. This doc is just about the Figma file structure.

---

## TL;DR — the fastest path

1. **Skim `source_design_doc.md`** to understand the product (5 min).
2. **Open `prototype/OPPO Installer Wizard.html`** in a browser. Flip through every screen using the Tweaks panel's "Navigate" section.
3. **Screenshot each screen** at 1× (1180×820 px) in your chosen aesthetic direction. There are 23 screens — see the list below.
4. **Create the Figma file** following the structure in this doc: 6 pages, styles + variables for tokens, a Components page for shared elements, and one page per wizard step.
5. **Drop screenshots in as references**, then rebuild each screen with real Figma layers using your styles and components. This is the part where you enrich the UI — replace placeholder mockups with real visuals, polish iconography, add hover states, prototype connections.

If you want to skip steps 3-4 and jump straight to building, the **html.to.design** Figma plugin can convert each prototype HTML page into Figma layers automatically — see "Plugin shortcuts" below.

---

## 1 · File structure

Create a Figma file named **"OPPO Installer Wizard"** with these pages, in order:

```
🟧 Cover                 — title + brand + version + status of the design
🎨 Design system         — color styles, type styles, effect styles, grid
🧩 Components            — every reusable component (chain, stepper, tiles, etc.)
🪟 01 · Shell            — Windows chrome + header + footer in isolation
🧭 02 · Step 0 — Prereq        (2 screens)
🖥️ 03 · Step 1 — Kodi box      (4 screens)
📺 04 · Step 2 — TV            (7 screens)
💿 05 · Step 3 — Player        (3 screens)
🔌 06 · Step 3.5 — Inputs      (4 screens)
✅ 07 · Test                   (3 screens)
🔁 08 · Flows                  — prototype-mode connections between all screens
📓 09 · Notes / archive        — scratch / iterations / things you rejected
```

Use the page emojis — they make the file scannable in a long file list, which this one will be.

---

## 2 · Frames per screen

Every screen frame is **1180 × 820 px**. That matches the prototype's default window size. Use these frame names verbatim so screenshots from the prototype can be auto-matched if you use html.to.design:

```
step0_gate
step0_exit
step1_intro
step1_tierA
step1_tierB
step1_tierC
step2_brand
step2_model
step2_notfound
step2_probe
step2_adb_warn
step2_test
step2_fail
step3_brand
step3_test
step3_fail
step35_intro
step35_ask
step35_fallback
step35_done
test_setup
test_confirm
test_success
```

Lay frames out in a single horizontal row per page, with 80 px gap between them. That gives a nice scroll-through-the-flow effect when reviewing the page.

---

## 3 · Local styles

Set up **color, type, and effect styles** before building anything. This makes the rest of the file refactorable. Use Figma **Variables** for colors and Figma **Local Styles** for type and effects.

### 3a · Color variables

Create **two collections** in Variables:

**Collection 1 — `Tokens`** (semantic, used by everything in components)

Mode-aware variables — define them once, give them values per mode. Create these variables with these names:

```
bg/desktop          background under the window
bg/window           window body bg
bg/titlebar         Windows title bar
surface/default     card / panel bg
surface/2           secondary surface
surface/sunken      inset / sunken bg
text/default        primary text
text/soft           secondary text
muted/1             muted text
muted/2             extra-muted
border/default      borders
border/strong       stronger borders
accent/default      brand accent (the orange/amber/sage)
accent/hover        accent darker
accent/soft         accent tinted background
accent/text         text on accent fill (usually #fff or near-black)
success/default
success/soft
warn/default
warn/soft
danger/default
danger/soft
info/default
info/soft
```

**Collection 2 — `Aesthetic`** (variant selector)

Add a variable mode-switcher to toggle between **Direction A** / **Direction B** / **Direction C**. Each mode in this collection feeds the `Tokens` collection above. This is how Figma Variables let you do the equivalent of the prototype's `body.theme-x.mode-y` swap.

Add a second mode dimension for **Light** / **Dark**. So your final modes are `A-Light`, `A-Dark`, `B-Light`, `B-Dark`, `C-Light`, `C-Dark`.

Values for each mode are in `README.md` § Design tokens, copied straight from `prototype/styles.css`. Direction A is the recommended default — populate that first if you want to ship faster.

### 3b · Type styles

Per aesthetic direction. Create three sets, prefixed:

**Direction A** (DM Sans + JetBrains Mono):

```
A · Display/Hero        DM Sans 700, 30 / 36, tracking -0.025em
A · Title/Screen         DM Sans 600, 26 / 32, tracking -0.02em
A · Title/Section        DM Sans 600, 15 / 22
A · Title/Sub-uppercase  DM Sans 600, 12 / 16, letter-spacing 0.06em, uppercase
A · Body/Lede            DM Sans 400, 15 / 24
A · Body/Default         DM Sans 400, 13 / 20
A · Body/Tile            DM Sans 600, 14.5 / 20
A · Body/Tile-desc       DM Sans 400, 12.5 / 18
A · Label/Field          DM Sans 500, 12.5 / 16
A · Label/Hint           DM Sans 400, 12 / 16
A · Eyebrow              DM Sans 600, 12 / 14, letter-spacing 0.08em, uppercase
A · Mono/Detail          JetBrains Mono 400, 11.5 / 16
A · Mono/Code            JetBrains Mono 400, 12.5 / 18
A · Mono/Kbd             JetBrains Mono 500, 11 / 14
```

Same pattern for **Direction B** (Space Grotesk) and **Direction C** (Plus Jakarta Sans). Copy the table and swap the family + letter-spacing per direction.

### 3c · Effect styles

```
Shadow/Card          0 1px 3px rgba(40,30,20,0.06)              (Direction A)
Shadow/Elevated      0 6px 24px -8px rgba(40,30,20,0.18), 0 2px 6px rgba(0,0,0,0.06)
Shadow/Window        0 24px 70px -20px rgba(40,30,20,0.45), 0 6px 14px rgba(0,0,0,0.08)
Shadow/Window-B      0 32px 100px -24px rgba(0,0,0,0.7), 0 8px 20px rgba(0,0,0,0.25)
Shadow/Window-C      0 30px 80px -24px rgba(20,50,30,0.4), 0 8px 18px rgba(0,0,0,0.1)
Glow/Accent (B-Dark) 0 0 24px var(accent-soft), 0 0 0 4px var(accent-soft)
Blur/Card (B only)   backdrop-filter blur 12-20 — Figma "Background blur" 12-20
```

### 3d · Corner radius variables

```
radius/window  14 (A) / 18 (B) / 16 (C)
radius/card    14 / 18 / 16
radius/button  10 / 12 / 12
radius/input   10 / 12 / 12
radius/chip    999 (pill)
```

### 3e · Spacing scale (use Number variables)

The prototype is permissive — values are situational. Establish a simple scale and stick to it:

```
space/4    space/6    space/8    space/10
space/12   space/14   space/16   space/18
space/20   space/24   space/28   space/32   space/40
```

---

## 4 · Components to build

All on the `🧩 Components` page. Use **Auto Layout** for everything — no fixed positioning. Use **Variants** where indicated.

| Component | Variants / properties | Notes |
|---|---|---|
| **Title bar** | none | 36 px tall. Slots: title text + title icon. |
| **Title-bar button** | type: `min` / `max` / `close`; hover boolean | 46 px wide × full height. Close turns red on hover. |
| **App icon** | none | 14 × 14 rounded square, accent → accent-hover gradient, "O" letter. |
| **Chain node** | state: `idle` / `active` / `done` / `gated`; icon: token list | 36 px icon + label below. See "icon set" below. |
| **Chain edge** | state: `idle` / `done` / `active` / `bidir` | 32 px line. `active` has animated gradient (use Smart Animate). |
| **Stepper item** | state: `idle` / `active` / `done` | dot + label. |
| **Stepper separator** | state: `idle` / `done` | 18 × 1 px line. |
| **Sidebar step** | state: `idle` / `active` / `done` | Used in the sidebar progress variant. |
| **Minimal progress bar** | `progress` (number) | Step name + counter + 200 px thin progress bar. |
| **Button** | kind: `primary` / `outline` / `ghost` / `danger`; size: `sm` / `md` / `lg`; iconLeft / iconRight booleans | The core action element. Direction C has a gradient + 2 px bottom "lip" variant — make it a separate variant if you support multiple directions. |
| **Tile** | state: `idle` / `selected` / `hover`; badge: `none` / `recommended` / `advanced` | Big clickable option (used in tier select, etc.). 18 × 20 padding, 14 px radius. |
| **Brand pill** | state: `idle` / `selected` | 14 × 8 padding, letter-logo + name + hint. |
| **HDMI tile** | state: `idle` / `selected`; number: 1-4 | Big number + "HDMI N" label. |
| **Filter pill** | state: `idle` / `selected` | Year/size filter chips. |
| **Card** | variant: `default` / `flat` / `selected`; padding: `default` / `compact` | Container primitive. |
| **Callout** | kind: `info` / `warn` / `success` / `danger` | Icon + body. |
| **Chip** | kind: `default` / `accent` / `success` / `warn` / `danger`; withDot boolean | Inline status pill. |
| **DiagLog header** | status: `idle` / `running` / `pass` / `fail` | Header row of the diagnostic log. |
| **DiagLog row** | status: `pending` / `run` / `pass` / `warn` / `fail` | A single check row. |
| **DiagLog footer** | kind: `default` / `success` / `fail` | Closing line of the diagnostic log. |
| **Input** | state: `default` / `focus` / `error`; type: `text` / `password` / `path` | Text inputs. Path/IP inputs use JetBrains Mono. |
| **Model row** | state: `idle` / `selected` | Row in the scrollable TV model list. |
| **Fallback rung** | status: `active` / `next` / `exit`; number 1-4 | Step rung in ADB-weak fallback funnel. |
| **Question row** | answered: `null` / `yes` / `no` | Yes/no row for test_confirm. |
| **Instruction step** | number 1-N | Numbered step circle + title + desc (used in test_setup "own" mode). |
| **Path row** | platform name | Card showing a platform + main path + keymap path. |
| **TV mockup** | screen content: `idle` / `mute` / `prompt` / `switched-to-N` | Decorative TV. |
| **Player mockup** | state: `standby` / `wake` / `on` | Decorative player. LED color changes. |
| **Footer nav** | hasBack boolean, hasNext boolean, nextLabel text | The back/continue row. |
| **App shell** | progress variant: `stepper` / `sidebar` / `minimal` | The whole window scaffold; slot for content. |

### Icon set

The prototype uses 30+ inline SVG icons in `shell.jsx`. They're all 24 × 24 viewBox, 1.8 stroke. Names:

```
media · kodi · tv · player · avr · hdmi · play · check · cross
chevR · chevL · chevD · refresh · search · info · warn · spark
folder · file · terminal · network · download · plug · remote
arrows · bolt · power · close · min · max
```

**Recommendation**: don't recreate these by hand. Use **Lucide** (or Phosphor) — the names map almost 1-to-1:

| Prototype | Lucide |
|---|---|
| `media` | `hard-drive` |
| `kodi` | `tv-minimal-play` |
| `tv` | `tv` |
| `player` | `boombox` or `disc-3` |
| `avr` | `audio-waveform` |
| `hdmi` | `cable` |
| `play` | `play` |
| `check` | `check` |
| `cross` | `x` |
| `chevR / chevL / chevD` | `chevron-right / left / down` |
| `refresh` | `refresh-ccw` |
| `search` | `search` |
| `info` | `info` |
| `warn` | `triangle-alert` |
| `spark` | `sparkles` |
| `folder` | `folder` |
| `file` | `file` |
| `terminal` | `terminal` |
| `network` | `globe` |
| `download` | `download` |
| `plug` | `plug` |
| `remote` | `remote-control` |
| `arrows` | `arrow-left-right` |
| `bolt` | `zap` |
| `power` | `power` |

Install the **Lucide Icons** Figma plugin and drop them in — you'll have parity with the prototype in a few minutes.

---

## 5 · Plugin shortcuts

Worth installing:

| Plugin | Why |
|---|---|
| **html.to.design** | Paste the prototype URL or HTML file → converts each frame to real Figma layers. Saves you 80% of the layer-building work. Quality varies; clean up shadows/text manually. |
| **Lucide Icons** | The icon library you'll want (see mapping above). |
| **Variables Importer** | Bulk-import the design tokens from a JSON file instead of clicking through Variables panel. Export from `styles.css` → JSON via a quick script, then import. |
| **Figma Tokens / Token Studio** | If your real codebase already uses design tokens (Style Dictionary etc.), Token Studio is the bridge for keeping Figma and code in sync. |
| **Iconify** | If you want broader icon search beyond Lucide. |
| **Autoflow** | For drawing prototype connection arrows between screens on the `Flows` page. |

---

## 6 · Recommended workflow

### Phase 1 — Setup (1 hour)
1. Create file + pages per § 1.
2. Set up color variables for **Direction A only** (modes: A-Light, A-Dark). Skip B and C initially.
3. Set up type styles for Direction A.
4. Set up effect styles + radius variables.

### Phase 2 — Component library (3-4 hours)
5. Build core primitives first: Button, Card, Callout, Chip, Input.
6. Then composites: Tile, Brand pill, HDMI tile, Model row, Question row.
7. Then the shell: Title bar, App header (chain + stepper), Sidebar, Footer nav.
8. Then DiagLog (header, row, footer separately).
9. Then mockups: TV, Player.

### Phase 3 — Screens (4-6 hours, depending on how much you enrich)
10. For each of the 23 screens: drop reference screenshot in, build the layout using components from § 4, then delete the screenshot.
11. Add screens in flow order — Step 0 first, Test last. Each screen will get faster as your component library matures.

### Phase 4 — Enrichment (open-ended)
This is where Figma earns its keep over the HTML prototype. Things to consider:

- **Real device illustrations** instead of CSS mockups. A drawn TV with stand and bezel. A drawn OPPO front panel with the LED and display.
- **Richer iconography**. Replace the line icons with a more brand-aligned set (filled + accent dot, or duotone, or hand-drawn).
- **Brand wordmarks** for TV/player brand pills (Sony, Samsung, LG…) instead of letter-on-tile. Get logos from each brand's brand resource page (use legally-licensed marks only).
- **Empty / loading / error states** the prototype doesn't show. Step 1 Tier A with all 3 checks failing. Step 3 with player offline. Step 0 exit branch when the user has no SMB knowledge at all.
- **Hover and pressed states** as separate frames or interactive components.
- **Polish microinteractions**. The chain edge animation, the diag log spinner, the screen-entry transition — all can be expressed in Smart Animate.

### Phase 5 — Prototype mode
12. On the `🔁 08 · Flows` page, duplicate every screen frame (or use the originals) and wire up Figma's prototype connections.
13. Map every button click in the doc's flow chart to a prototype interaction:
    - Step 0 gate → Continue → Step 1 intro
    - Step 0 gate → Not yet → Step 0 exit
    - Step 1 intro → Tier A tile → Step 1 Tier A
    - …(see screen flow chart in `README.md`)
14. Use Smart Animate on screen transitions (300 ms ease).
15. Add overlay-style modals for things like the ADB allow-debug heads-up if you want a different reading.

---

## 7 · Screen-by-screen layout cheatsheet

Each screen follows the same outer template. Inside, the layout is one of three patterns:

### Pattern A — Hero screen (intro / success)

Used by: `step0_gate`, `test_success`

Vertical centered hero, max-width 660 px:
```
eyebrow             [Eyebrow style, accent color]
title (30 px / 700) [Display/Hero]
body (15.5 px)      [Body/Lede]
checklist card      [Card with 3 rows]
button row          [Primary + Ghost]
```

### Pattern B — Two-column work screen

Used by: `step1_tierA/B/C`, `step2_probe`, `step2_test`, `step2_adb_warn`, `step3_test`, `step35_intro`, `step35_ask`, `step35_done`, `test_setup`

```
screen-header
  h1 (26 px)
  subtitle (15 px, max-width 620)
two-column grid (1.1fr 1fr, 20 px gap, items start)
  left column   — input / interaction
  right column  — feedback / context
footer nav
```

### Pattern C — Single-column choice list

Used by: `step0_exit`, `step1_intro`, `step2_brand`, `step2_model`, `step2_notfound`, `step3_brand`, `step3_fail`, `step35_fallback`, `test_confirm`

```
screen-header
content (mixed; usually a stack of tiles or a brand grid)
footer nav
```

---

## 8 · Layout details for tricky screens

### `step0_gate` (Pattern A — hero)

- Window 1180 × 820
- Header (chain + stepper) ~110 px
- Hero column max-width 660 px, **centered horizontally**, 80 px top padding
- Checklist card: surface bg, 18 × 22 padding, 14 px radius, 3 rows of 13.5 px text with `→` accent-colored prefix

### `step1_tierA` (Pattern B)

- Header
- Two columns:
  - **Left**: Card titled "SSH credentials" — fields: Username (text), Authentication (segmented: Password / SSH key), Password (text), button "Test connection"
  - **Right**: DiagLog with 3 checks (SSH reachable / userdata writable / restart available); after test, an info callout below
- Footer nav (Back / Continue to TV — disabled until test passes)

The diag log row animation is key: each row goes `pending` → `running` (spinner) → `pass` (✓). Build the row as 3 variants and use Smart Animate.

### `step2_model` (Pattern C with filters)

Structure top-to-bottom:
1. Search input row with "Can't find my model" link on the right
2. Year filter row: label "Year" + filter-pill row (2025…2018)
3. Size filter row: label "Size" + filter-pill row (43"…85")
4. Model list (scrollable, max-height 320 px, 1 px borders between rows, 14 px radius outer)

### `step35_ask` (Pattern B)

Left column:
- HDMI tile grid 4-wide (HDMI 1, 2, 3, 4) — big numbers, hover lifts, selected = accent-soft bg
- Outline button "Not sure — find it for me"

Right column:
- TV mockup (16:10 aspect)
- After pick: info callout + Yes/No buttons; after confirm: large primary "Next"

This screen has **two iterations** in the prototype (capture OPPO, then capture Kodi). In Figma, build two frames — `step35_ask_oppo` and `step35_ask_kodi` — and wire them in flow mode.

### `test_setup` (two-state)

State 1 — mode picker (one tile-grid):
- Two tiles: "Use our test disc" / "Use one of your own files"

State 2a — disc mode:
- Left card: location picker, warning callout, Copy button → diag log
- Right card: "What this verifies" (4 chain check rows)

State 2b — own mode:
- Left card: 4 numbered instruction steps + an info callout
- Right card: "What this verifies" + a small "Kodi box → Play any UHD ISO" status card

Build all three states as separate frames; wire with prototype interactions.

### `test_confirm`

Three question rows stacked. Each row is a tile with:
- Left circle (number, turns ✓ green or ✕ red after answer)
- Title (the question)
- Description ("Failure routes to → Step N · …")
- Right: Yes / No filter pills

Footer button label changes based on answers: "See the summary" / "Fix routing → Step 3" / etc.

---

## 9 · Flow connections (for prototype mode)

```
step0_gate ──(Continue)──> step1_intro
step0_gate ──(Not yet)────> step0_exit
step0_exit ──(Back)───────> step0_gate

step1_intro ──(Tier A)────> step1_tierA
step1_intro ──(Tier B)────> step1_tierB
step1_intro ──(Tier C)────> step1_tierC
step1_tier*  ──(Continue tested)──> step2_brand

step2_brand ──(brand pick)─> step2_model
step2_model ──(model pick + Continue)──> step2_adb_warn
step2_model ──(Can't find)──> step2_notfound
step2_notfound ──(Probe)──> step2_probe
step2_notfound ──(Manual)──> step2_adb_warn
step2_probe ──(Use Roku ECP)──> step2_test
step2_adb_warn ──(I'm ready)──> step2_test
step2_test ──(Yes)─────> step3_brand
step2_test ──(No)──────> step2_fail
step2_fail ──(any tile)──> step3_brand  (with state flag)

step3_brand ──(Continue)──> step3_test
step3_test ──(success Continue)──> step35_intro
step3_test ──(Test didn't work)──> step3_fail
step3_fail ──(Retry)──────> step3_test

step35_intro ──(Capture inputs)──> step35_ask  OR  step35_fallback  (state-dependent)
step35_ask ──(after both inputs captured)──> step35_done
step35_fallback ──(any rung)──> step35_done
step35_done ──(Continue)──> test_setup

test_setup ──(Use test disc)──> test_setup [disc mode]
test_setup ──(Use own file)──> test_setup [own mode]
test_setup ──(I played it)──> test_confirm

test_confirm ──(all yes)──> test_success
test_confirm ──(play=no)──> step3_test
test_confirm ──(switch=no)──> step2_test
test_confirm ──(menu=no)──> step1_intro

test_success ──(Done)──> step0_gate (reset)
```

Wire these on the `🔁 08 · Flows` page.

---

## 10 · Things to NOT do

- **Don't try to ship all three aesthetic directions in Figma.** Pick one. Variables make multi-mode possible but it triples your component variant count. If you really want all three, do A fully, then duplicate the file for B and C as alternates.
- **Don't recreate the inline SVG icons by hand.** Use the Lucide plugin (§ 4).
- **Don't replicate the Tweaks panel.** It's a design-time aid in the prototype, not a feature of the actual app.
- **Don't draw a fake OPPO logo or TV brand logos.** Use the real wordmarks (per each brand's brand-resource page) or stay generic with letter-on-tile.

---

## 11 · When you're done

- **Publish the Components page as a Library** so any other Figma files can pull these components.
- **Connect to the codebase via Figma Dev Mode** — annotate frames with component names matching the implementation.
- **Export the design tokens** (Variables) as JSON via Token Studio or Variables Importer; feed them into the real app's design system so colors and spacing stay in sync.

The HTML prototype in `prototype/` is a reference — once your Figma file is the source of truth, you can update the HTML or retire it.
