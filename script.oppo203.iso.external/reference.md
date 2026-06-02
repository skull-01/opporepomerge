# Version 2.5.2 Build 1 — OPPO/Chinoppo NAS Playback Capability Gates

This build converts the v45 AutoScript / M9702 / TrueNAS / NFS research into software gating rules only. Original OPPO UDP-203/UDP-205 NAS playback support is gated behind jailbreak plus AutoScript-capable firmware, with `20X-56` treated as the minimum and `20X-65-0131` as the recommended jailbreak target. Firmware `20X-54-1127` and older/pre-56 firmware are blocked for AutoScript-based workflows.

Chinoppo-family support is treated as a capability-gated family rather than a single-version firmware rule because the active patched firmware/binary determines available behavior. M9201, M9203, M9205C, M9702, IPUK-UHD8592, GIEC-BDP-G5300, and Magnetar-UDP800 style profiles are candidate clone-family profiles that require user/device confirmation before claiming per-model support.

The user confirmed that NAS-mounted file playback works. This build records that as capability evidence but does not claim universal hardware validation.

---

# Version 2.5.0 Build 1 — v2.5 development baseline

Build 1 starts the v2.5 series from the v2.2.0 software-merge baseline. It is intentionally low risk: version metadata, v2.5 planning/tracking documentation, release-audit evidence, packaging, and verification are updated while runtime behavior is preserved.

Current v2.5 focus areas:

- Stability-first enhancement.
- User experience and wizard refinement.
- Diagnostics and supportability.
- Hardware-validation-driven fixes after user testing.

Real hardware validation remains pending and must be recorded in `HARDWARE_VALIDATION_TRACKER_v2.5.0.md`.

---

## V45 User-Supplied Research Addendum — AutoScript, M9702 Network Playback, TrueNAS/NFS, and Kodi Path Mapping

Source file integrated into this handoff: `oppo203_kodi_external_player_reference.md`.

Status: research/reference material only. This addendum should guide future planning around AutoScript, M9702 network playback, TrueNAS/NFS layout, and Kodi-to-player path translation. It does not change runtime behavior and does not prove a final command/API for launching arbitrary NAS-mounted media on real hardware.

### Verbatim research content begins

# Oppo 203 / M9702 Network Playback and Autoscript Reference for Kodi Add-on Design

This document reorganizes the researched information into a technical reference intended for designing a Kodi add-on that can use an Oppo UDP-203 class player or an M9702 clone as an external player over the local network.[cite:1][cite:20][cite:21]

The focus is on the Oppo/M9702 jailbreak ecosystem, autoscript behavior, SMB/NFS playback, TrueNAS SCALE integration, and the practical implications for a Kodi external-player workflow.[cite:1][cite:22][cite:23][cite:39]

## Scope and target use

The M9702 is widely described as an Oppo UDP-203 clone and is commonly used with community jailbreak firmware and autoscripts to unlock expanded playback, region switching, network playback, and debug functionality.[cite:18][cite:20][cite:21]

For Kodi integration purposes, the most relevant outcome is that the player can act as a dedicated network playback endpoint that reads media directly from SMB or NFS shares while maintaining Oppo-class disc-style playback behavior for ISO, BDMV, UHD, HDR, and some Dolby Vision use cases.[cite:20][cite:21][cite:22]

## Device and firmware model

### Oppo jailbreak autoscript model

In the Oppo jailbreak community, an autoscript is generally a boot-time script that selects and launches a patched player binary instead of the stock binary, often by checking for a marker file or loading an alternative executable from a writable boot location.[cite:1]

A common pattern discussed in forum materials is a shell-script wrapper around `bdpprog` that checks for a file such as `/mnt/ubi_boot/.debugstart`, optionally launches `bdpprog_debug`, and otherwise falls back to either a replacement `bdpprog` or the original `bdpprog.1` binary.[cite:1]

This means the autoscript layer is not the feature itself; it is the mechanism that ensures the desired patched runtime is activated automatically at boot.[cite:1]

### M9702-specific behavior

For the M9702, community reports describe autoscripts as a way to switch firmware behavior and launch selected binaries without repeatedly reflashing full firmware images.[cite:21]

This is significant for development work because a Kodi integration strategy should assume that the exact capabilities of the player depend on the currently active firmware/binary combination, not only on the underlying hardware.[cite:20][cite:21]

## Functional capabilities exposed by jailbreak firmware and autoscripts

The following capabilities are repeatedly associated with Oppo/M9702 jailbreak firmware and autoscript setups.[cite:1][cite:20][cite:21]

| Capability area | Practical effect | Relevance to Kodi external-player design |
|---|---|---|
| Alternative player binary boot | Patched player launches automatically at startup.[cite:1] | Kodi integration should assume player behavior may differ from stock firmware. |
| Region switching / region-free behavior | Blu-ray and related region restrictions can be removed or switched.[cite:20][cite:17] | Relevant if add-on exposes disc-image playback that depends on region handling. |
| ISO / BDMV / full-disc structure support | Full disc backups and folder structures are a key supported use case.[cite:20][cite:21] | Core reason to offload playback from Kodi to Oppo-class hardware. |
| Dolby Vision / HDR mode controls | Community reports mention Auto, TV-led, Player-led, and forced Dolby Vision modes on M9702 firmware builds.[cite:21] | Important for choosing when the add-on should delegate playback externally. |
| Network share playback | SMB and NFS playback are available in community builds and user reports.[cite:22][cite:25] | Essential for NAS-based playback workflows. |
| Telnet / debug access | Advanced users report telnet access in autoscript-enabled environments.[cite:25][cite:31] | Useful for automation, diagnostics, and recovery during integration work. |
| Persistent boot-time customization | Mounting shares, enabling debug modes, or selecting binaries can happen automatically at boot.[cite:1][cite:31] | Makes a stable Kodi-to-player appliance workflow realistic. |

## Network playback model

### What SMB and NFS provide

On the M9702, SMB and NFS enable the device to function as a network media endpoint that streams full-quality video directly from a NAS or server rather than from local USB storage.[cite:22][cite:25]

Review material and community discussion indicate that the player can browse network shares, buffer briefly, and then play large UHD files and full-disc structures from those shares.[cite:22]

For a Kodi add-on, this means the cleanest architecture is usually not “Kodi sends the media bytes to the Oppo,” but rather “Kodi instructs or prepares the Oppo to access media from a path that both systems can understand.”[cite:22][cite:23]

### SMB characteristics

SMB is useful because it integrates naturally with Windows-style file management and is convenient for loading or organizing media from desktop systems.[cite:33][cite:65]

However, Oppo-class devices are commonly reported to rely on older SMB behavior, including SMB1-era compatibility constraints and fragile authentication handling, which can make guest/public shares simpler than credential-based setups on embedded players.[cite:23][cite:26][cite:55]

### NFS characteristics

NFS is frequently recommended for Oppo-class playback because it avoids many SMB authentication issues and is often described as the smoother option on Linux-oriented NAS platforms.[cite:23][cite:33][cite:34]

OpenMediaVault guidance and community reports associated with Oppo 203-class clients specifically recommend NFSv2/v3 style compatibility rather than relying on NFSv4-only configurations.[cite:23]

For a Kodi external-player design, NFS is therefore the strongest candidate for the actual player-facing transport, even if SMB remains useful for desktop-side library management.[cite:23][cite:85]

## Telnet, SMB, and NFS together

Community discussion around the M9702 notes setups where telnet, NFS, and SMB all work together inside an autoscript-enabled environment.[cite:25][cite:31]

That combination is important because each protocol serves a different function:[cite:23][cite:31][cite:33]

- Telnet provides shell-level control for diagnostics, boot-time scripting, testing mounts, and recovering from configuration mistakes.[cite:31]
- NFS provides the most straightforward read path for media playback from NAS storage.[cite:23]
- SMB provides a user-friendly management path for copying, editing, or reorganizing media from PCs.[cite:33][cite:65]

For AI-readable system design, the resulting model is:

1. Manage files over SMB from a desktop or automation host.[cite:65][cite:85]
2. Expose the same media path over NFS to the Oppo/M9702 for playback.[cite:23][cite:82]
3. Use telnet and autoscript logic to ensure the player mounts the correct NFS path at boot and can be debugged if the mount fails.[cite:31]

## TrueNAS SCALE design pattern

### Recommended storage layout

For TrueNAS SCALE, the simplest and most maintainable design for this use case is one dedicated media dataset, such as `tank/media`, instead of many fragmented datasets.[cite:74][cite:79][cite:101]

That single dataset can then be exposed over both SMB and NFS, while keeping snapshots, scrubs, and replication easier to reason about.[cite:82][cite:85]

### Can one dataset be shared over multiple protocols?

TrueNAS supports sharing one dataset through both SMB and NFS at the same time, and community guidance describes this as a valid multiprotocol arrangement when permissions are managed carefully.[cite:85][cite:87]

It is also possible to expose the same dataset via multiple NFS shares with different access characteristics, such as one read-only export and one read-write export, while also serving the same underlying path over SMB.[cite:82][cite:106]

The main caution is that mixed-protocol write access can become confusing, so a safer media-library pattern is usually SMB read-write for content management and NFS read-only for playback devices.[cite:83][cite:87]

### Dataset and folder boundary rules

A single physical folder cannot belong to multiple datasets at the same time in ZFS/TrueNAS because each dataset is its own filesystem boundary.[cite:74][cite:79]

Child datasets can appear under a parent path, but they remain separate filesystems, which matters because SMB can often present them naturally as subfolders while NFS clients usually need separate exports and mounts for crossing filesystem boundaries.[cite:74][cite:72]

For Kodi add-on design, this implies that a flat, single-dataset media tree is simpler than a heavily nested multi-dataset tree if the external player will mount content through NFS.[cite:74][cite:79]

## TrueNAS SCALE share configuration model

### SMB share role

The SMB share should be treated as the management interface for the media dataset, typically used by desktop systems to add or edit files.[cite:65][cite:85]

On TrueNAS SCALE, a share can be created for `/mnt/tank/media`, marked browsable, and configured either for guest access on a trusted home LAN or for a dedicated authenticated media user.[cite:63][cite:66][cite:65]

Guest access is often the easiest path for Oppo-class embedded clients, but a dedicated user is cleaner if desktop systems also need controlled write access.[cite:55][cite:63]

### NFS share role

The NFS share should be treated as the player-facing playback interface.[cite:23][cite:39]

For Oppo/M9702 compatibility, the recommended pattern is an NFS export for the same dataset path, restricted to the local subnet, configured read-only for playback devices, and aligned with NFSv3-style operation where necessary.[cite:23][cite:39][cite:59]

OpenMediaVault guidance discussed in relation to Oppo-class devices recommends subnet restriction, read-only access, and options such as `insecure` when embedded clients require it.[cite:23]

### Guest SMB behavior vs NFS behavior

NFS does not normally prompt for a username or password in the same way SMB does; access is controlled by client IP and UID/GID mapping rather than interactive login prompts.[cite:57][cite:59][cite:60]

As a result, if an Oppo/M9702 user cannot enter credentials, the practical options are either an NFS export or an SMB guest/public share rather than expecting a full authentication UI on the player.[cite:55][cite:58]

## Best-practice topology for M9702 network playback

The most stable and developer-friendly topology identified in the research is the following.[cite:23][cite:85][cite:90]

| Component | Recommended role | Notes |
|---|---|---|
| TrueNAS SCALE | Central NAS and protocol server | Use static or reserved IP address.[cite:96][cite:104] |
| Media dataset | Single dataset such as `tank/media` | Easier snapshot and share management.[cite:74][cite:79] |
| SMB share | Desktop management plane, usually read-write | Used from PC/macOS/Linux to add files.[cite:65][cite:85] |
| NFS share | Player playback plane, usually read-only | Best fit for M9702/Oppo compatibility.[cite:23][cite:39] |
| M9702 autoscript | Boot-time NFS mount and player startup | Makes the device deterministic at startup.[cite:31][cite:25] |
| Telnet | Maintenance and debugging path | Used to inspect mounts, logs, and recovery actions.[cite:31] |
| Ethernet | Physical transport | Wired gigabit is preferred for UHD playback.[cite:90][cite:22] |

## Autoscript design for a TrueNAS SCALE + M9702 workflow

### Functional goal of the autoscript

In this use case, the autoscript should not be treated as a media indexer or library manager.[cite:1][cite:31]

Its job is much narrower and more useful:

1. Wait for the network and the NAS to become reachable.[cite:31]
2. Mount the TrueNAS NFS export to a fixed local path.[cite:23][cite:39]
3. Optionally log or expose mount failure through telnet-accessible diagnostics.[cite:31]
4. Launch the patched Oppo/M9702 player binary.[cite:1]

### Reference autoscript pattern

The following pattern captures the configuration that best matches the researched setup:[cite:23][cite:39][cite:31]

```sh
# Wait for network and NAS reachability
for i in 1 2 3 4 5; do
  ping -c1 -W1 192.168.1.10 && break
  sleep 2
done

# Create mountpoint
mkdir -p /mnt/nas/media

# Mount TrueNAS NFS export
mount -t nfs -o ro,nolock,vers=3,rsize=131072,wsize=131072,hard,intr \
  192.168.1.10:/mnt/tank/media /mnt/nas/media

# Optional sanity check
if ! mount | grep -q "/mnt/nas/media"; then
  echo "NFS mount failed"
fi

# Launch patched player binary using the firmware-specific path
# /mnt/ubi_boot/bdpprog
```

### Meaning of the mount options

| Option | Purpose | Reason in this environment |
|---|---|---|
| `ro` | Mount read-only | Matches playback-only role for the M9702.[cite:23] |
| `nolock` | Disable lock-manager dependence | Helps avoid lock-manager issues on embedded clients.[cite:23] |
| `vers=3` | Force NFSv3 | Oppo-class clients are commonly reported to behave better with NFSv2/v3-era compatibility.[cite:23] |
| `rsize=131072,wsize=131072` | Large I/O buffers | Suitable for large 4K/UHD sequential reads.[cite:39] |
| `hard,intr` | Stable mount behavior with interruptibility | Supports resilience during short network faults.[cite:39] |

For AI system design, the stable abstraction is that the M9702 should always see the NAS content at one deterministic internal path, such as `/mnt/nas/media`, regardless of where the content lives physically on the NAS.[cite:31][cite:39]

## Implications for Kodi add-on development

### Likely integration architecture

The research supports an architecture where Kodi acts as the control plane and the Oppo/M9702 acts as the playback plane.[cite:22][cite:23][cite:31]

This suggests the following logical design:

1. Kodi stores or derives a NAS-backed media path for the selected item.[cite:22][cite:85]
2. The M9702 already has that NAS content mounted locally via autoscript and NFS.[cite:23][cite:31]
3. Kodi launches the external player using a path or command that corresponds to the M9702-visible namespace.[cite:22][cite:31]

This is more robust than trying to stream through Kodi into the Oppo because the Oppo/M9702 ecosystem is already optimized for direct network playback from shares.[cite:22][cite:25]

### Path-mapping requirement

A Kodi add-on intended to use an Oppo/M9702 as an external player will likely need a deterministic path-mapping layer.[cite:22][cite:31]

For example, Kodi may know a file as one of the following:

- `smb://truenas/media/Movies/MovieName/movie.mkv`
- `/mnt/media/Movies/MovieName/movie.mkv`
- a database library reference

The external-player bridge will likely need to translate that to the path visible inside the Oppo/M9702 environment, such as:

- `/mnt/nas/media/Movies/MovieName/movie.mkv`

That translation layer is one of the most important implementation details implied by the network-play model described in the research.[cite:22][cite:23][cite:31]

### Why one shared dataset matters for add-on design

A single TrueNAS media dataset exposed consistently over SMB and NFS simplifies path translation because the logical tree stays the same across management and playback protocols.[cite:74][cite:79][cite:85]

If the NAS uses many child datasets that appear as separate filesystems, the add-on may need dataset-aware path rules, especially if the player mounts each NFS export separately.[cite:74][cite:72]

### Why read-only NFS is preferred for the player

Using read-only NFS for the M9702 reduces accidental library modification and lowers the complexity of mixed-protocol permission conflicts.[cite:82][cite:83][cite:87]

For a Kodi external-player workflow, the player should behave as a pure consumer of media, not as a system that writes metadata, renames files, or changes library state on the NAS.[cite:82][cite:85]

## Practical recommendations for implementation planning

### Recommended baseline configuration

| Area | Recommended baseline |
|---|---|
| NAS OS | TrueNAS SCALE.[cite:101][cite:104] |
| Media storage | One dataset such as `tank/media`.[cite:74][cite:79] |
| Desktop file management | SMB share on the media dataset, read-write.[cite:65][cite:85] |
| Player media access | NFS share on the same dataset, read-only, subnet-restricted, NFSv3-compatible.[cite:23][cite:39] |
| Player boot behavior | Autoscript mounts NFS to a stable local path before launching the player binary.[cite:31][cite:39] |
| Diagnostics | Telnet enabled for inspection of mounts and recovery steps.[cite:25][cite:31] |
| Physical network | Wired gigabit Ethernet.[cite:90][cite:22] |

### Constraints and caveats

- Capability differences depend on the specific firmware build and active patched binary, not only on the device model.[cite:20][cite:21]
- SMB authentication UX on embedded Oppo-class devices is often weak, so guest SMB or NFS is usually easier than credential-heavy SMB workflows.[cite:23][cite:55][cite:58]
- A single folder cannot simultaneously belong to multiple ZFS datasets, so dataset planning affects how simple NFS path mapping will be.[cite:74][cite:79]
- Multiprotocol write access is possible but should be minimized for a media-library appliance design.[cite:83][cite:85][cite:87]

## Design assumptions an AI model can safely use

The following assumptions are strongly supported by the researched material and are suitable as working design inputs.[cite:1][cite:21][cite:85]

1. The Oppo/M9702 external-player environment should be modeled as a Linux-like appliance that can run boot-time shell logic and mount NFS shares.[cite:1][cite:31]
2. Direct NAS playback is the intended and most valuable playback model for the device class.[cite:22][cite:25]
3. The cleanest deployment path uses TrueNAS SCALE with one media dataset exposed through SMB for management and NFS for playback.[cite:82][cite:85]
4. The autoscript should make the NAS media tree appear at a fixed local mountpoint on the player every time it boots.[cite:31][cite:39]
5. Any Kodi integration layer should prioritize deterministic path translation over media proxying or transcoding.[cite:22][cite:23]

## Open questions for engineering follow-up

The research supports the storage and playback model, but several integration details still require direct device-level testing.[cite:21][cite:31]

- What exact command, URI, or file-open mechanism can an Oppo 203 or M9702 accept from an external controller?[cite:31]
- Whether the player can be triggered through telnet, HTTP, IR emulation, or another remote-control interface was not established in the researched material and needs separate validation.[cite:31]
- Whether Kodi should launch the player by path, by menu-state automation, or by a remote API remains an implementation question outside the confirmed material here.[cite:31]

Those are the key unknowns that would determine the final architecture of a Kodi add-on intended to use an Oppo/M9702 as an external player.

### Verbatim research content ends

---

# Version 2.2.0 Build 9 — Merge test-parity audit checkpoint

Build 9 is a narrow v1.1.9 + v0.9.14 superset-merge slice.  It does not broaden runtime behavior.  It records a test-parity audit of already protected v0.9.14 hardware-compatibility behavior and remaining merge work before a merge-complete candidate.

Key points:

- Adds `MERGE_PARITY_AUDIT_v2.2.0_BUILD9.md`.
- Keeps the full merge in progress, not complete.
- Preserves the 99 percent coverage gate.
- Preserves the self-contained handoff reconstruction rule for future builds.
- Does not perform real hardware testing.

Required verification:

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0.9
```

# Version 2.2.0 Build 8 - Merge parity audit and self-contained handoff reconstruction

Build 8 continues the gradual v1.1.9 + v0.9.14 superset merge with a narrow merge-parity audit checkpoint. It also starts the forward rule that the latest AI handoff Markdown must contain a copy/paste resume prompt at the top and a reconstruction bundle for the latest build source tree.

## Build 8 verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests
python -m coverage run -m pytest -q
python -m coverage report -m
python tools/audit_release.py --expected-version 2.2.0.9
```

## Build 8 scope

- Adds `MERGE_PARITY_AUDIT_v2.2.0_BUILD8.md`.
- Keeps the full merge in progress, not complete.
- Preserves the 99 percent coverage gate.
- Requires the v22 handoff to include reconstruction data and a resume prompt at the top.
- Does not claim real hardware validation.

## Version 2.2.0 Build 7 technical notes

Build 7 is a narrow service-watcher persistence hardening slice for the gradual v1.1.9 + v0.9.14 superset merge. The main code change is defensive: `settings_reader.save_settings()` now returns `False` when the add-on-data directory is blank, preventing accidental writes to a relative `settings.xml` in the current working directory.

The service watcher behavior is locked down with tests for:

- failed persistence logging without repeated save loops,
- in-memory clone preset application when persistence is unavailable,
- stock OPPO jailbreak toggle persistence to `oppo_http_payload_mode=json_payload`, and
- no broad/full merge behavior.

The 99% coverage gate remains enforced. Reavon remains warning-only; Chinoppo/M9702 command behavior remains model-gated.

---

## Version 2.2.0 Build 6 technical notes

### Design decision

Build 6 keeps the merge narrow by wiring v0.9.14 compatibility-warning surfacing into the active v1.x wizard hardware-selection path without replacing the wizard implementation. The new active-wizard adapter is warning-only: it collects warnings from `first_run_wizard.collect_compatibility_warnings()` and surfaces them through a small UI adapter, but it does not automatically apply compatibility presets or change the existing Chinoppo preset confirmation flow.

### Affected modules

- `resources/lib/wizard.py`: added `_AddonSettingsAdapter`, `_WizardUiAdapter`, `_wizard_log()`, and `_surface_hardware_compatibility_warnings()`.
- `tests/test_superset_merge_build6.py`: verifies active wizard warning surfacing, Reavon no-mutation behavior, AutoScript warning surfacing, and import-failure safety.

### Invariants

- Reavon remains warning-only.
- Reavon command maps are not bundled or mutated.
- Chinoppo/M9702 wake/preset behavior remains model-gated.
- Warning surfacing never blocks wizard completion.
- The 99% coverage gate remains enforced.

### Deferred work

The full wizard replacement/union is still deferred. Future merge slices can continue reconciling remaining v0.9.14 wizard behavior into the active v1.x wizard gradually.

---

## Version 2.2.0 Build 5 technical notes

### Design decision

Build 5 keeps the merge narrow by adding testable v0.9.14 wizard/UI compatibility-warning surfacing helpers instead of replacing the active v1.x wizard. The helper surface is intentionally small: collect/apply compatibility behavior, log warnings with `[v0.9.14-warning]`, display warnings through optional UI methods, validate hardware-choice answers, and swallow UI failures so configuration warnings cannot break playback or settings changes.

### Affected modules

- `resources/lib/first_run_wizard.py`: added `surface_compatibility_warnings()`, `ask_choice()`, and `apply_and_surface_compatibility()`.
- `tests/test_superset_merge_build5.py`: verifies UI fallback paths, logging, clone preset application, AutoScript warning surfacing, and Reavon warning-only behavior.

### Invariants

- Reavon remains warning-only.
- Reavon command maps are not bundled or mutated.
- Chinoppo/M9702 wake/preset behavior remains model-gated.
- Warning surfacing never raises to callers.
- The 99% coverage gate remains enforced.

### Deferred work

The active wizard flow is not broadly rewritten in this build. Future merge slices can wire these helpers into a richer wizard/UI path once tests are in place.

---

## Version 2.2.0 Build 4 technical notes

Build 4 ports a narrow persistence behavior into the gradual v1.1.9 + v0.9.14 superset merge. The service watcher restored in earlier v2.2 builds now writes applied compatibility preset changes back to the add-on data `settings.xml` when a preset actually mutates settings.

### Design decision

The watcher remains failure-safe. Persistence only runs when `apply_compatibility_preset()` returns mutations and an `addon_data_dir` is available. Save failures are logged and do not break service settings changes.

### Reavon invariant

Reavon remains warning-only. Because Reavon preset handling returns only the warning marker and no command mutations, the Build 4 persistence path does not create or save OPPO command-map changes for Reavon models.

### Tests

Build 4 adds tests for XML persistence, existing-row updates, runtime/private-key skipping, clone-preset persistence, and Reavon no-mutation behavior.

## Version 2.1.0 Build 5 technical notes - 98 percent coverage gate

Build 5 is a controlled coverage-hardening increment on top of v2.1.0 Build 4. It raises the enforced total `resources/lib` coverage gate to 98% while preserving the existing v2.0/v2.1 runtime behavior.

The added tests target meaningful defensive paths in OPPO protocol parsing/discovery, external-player cleanup and hold modes, installer dispatch/error branches, settings parsing, logging rotation/format fallback, and playercorefactory merge deduplication. No tests require real OPPO hardware, Kodi, TCL/Android TV, or ADB.

```ini
fail_under = 98
```

The full v1.1.9 + v0.9.14 superset merge remains deferred until after the gradual 99% coverage hardening track.

## Version 2.1.0 Build 4 technical notes - 97 percent coverage gate

Build 4 is a controlled coverage-hardening increment on top of v2.1.0 Build 3. It raises the enforced total `resources/lib` coverage gate to 97% while preserving the existing v2.0/v2.1 runtime behavior.

### Design rule

The tests added in this build focus on existing behavior and defensive paths: installer preview/apply branches, disabled diagnostic safeguards, OPPO HTTP track helper branches, file-list parser edge cases, verbose-push timeout handling, preflight failure handling, TCP-client timeout/cleanup handling, and custom preset load/merge validation.

### Scope boundary

This build does not start the full v1.1.9 + v0.9.14 merge. It is only a pre-merge coverage-hardening step toward the later 99% target.

### Coverage gate

`.coveragerc` now enforces:

```ini
fail_under = 97
```

## Version 2.1.0 Build 3 technical notes - 96 percent coverage gate

Build 3 is a controlled coverage-hardening increment on top of v2.1.0 Build 2. The design rule remains: tests must exercise meaningful behavior, not merely execute lines.

### Coverage strategy

The build targets previously under-covered branches in existing MVP-support modules: `oppo_control`, `oppo_tcp_client`, `settings_reader`, `tv_control`, `reconnect_backoff`, `arch_benchmark`, `autoscript_helper`, `wizard_polish`, `logging_v116`, `playercorefactory_merge`, and `preset_manager`.

### Bug fixed

`oppo_control.discover_oppo()` previously assumed the UDP socket variable existed in the `finally` cleanup path. If top-level UDP socket creation failed, cleanup could raise `UnboundLocalError`. Build 3 initializes the socket reference before the try block and only closes it when creation succeeded.

### Invariants preserved

- No full merge work was started.
- No real OPPO, TV, ADB, or Kodi runtime is required by the new tests.
- The enforced coverage gate is now 96%.
- The 99% target remains gradual pre-merge hardening work.

# Version 2.1.0 Build 1 technical notes

## Version 2.1.0 Build 2 technical notes - gradual 99% coverage path

Build 2 raises the coverage gate from 92% to 94% using behavior-focused tests rather than line-only execution. The added tests cover hermetic branches around AutoScript mount generation, discovery cache load/save edge cases, wizard GUI/no-GUI and benchmark fallbacks, OPPO remote error fallbacks, external-player idle/trick-play suppression logic, logging rotation, playercorefactory merge validation, and preset-manager validation.

The build intentionally does not start the full historical superset merge. The coverage target is now treated as a pre-merge hardening track: 94% in Build 2, with later builds expected to continue toward 99% in small increments.


Build 1 of the v2.1.0 hardening line addresses the 92 percent coverage gate that was explicitly deferred from the v2.0 MVP. The build starts from the final v2.0.0 release artifact and does not expand runtime feature scope.

## Coverage-gate design

The gate is now enforced in `.coveragerc` as `fail_under = 92` for `resources/lib` with branch coverage enabled. The new test work focuses on existing behavior and stubbed boundaries: Kodi imports, installer fallback paths, OPPO/TCP helpers, external-player branches, wizard helpers, and module edge cases.

## Bug found by coverage hardening

The new installer fallback test found that `resources/lib/installer.py` called `xbmc.log()` in the wizard auto-launch failure path without importing `xbmc`. The production fix is a direct guarded-runtime-compatible import in the module. This is a real stability fix, not just a coverage-only change.

## Invariants preserved

The v2 MVP behavior remains unchanged: External Player flow, M9702/Chinoppo wake rewrite, stock OPPO pass-through, TCL/Android TV ADB switching, fake OPPO server tests, session sentinel cleanup, command-map invariants, and Reavon warning-only behavior are preserved.


# Version 2.0.0 Final Release technical notes

This final v2.0.0 package is produced from the verified Build 6 line and restores the public add-on version identity to `2.0.0`. The change is packaging and release-identity focused; runtime MVP behavior is intentionally preserved.

## Final release decision

Build 6 demonstrated the stable build-id line. The release package uses that source as the baseline, updates `addon.xml` back to `2.0.0`, keeps Build 6 provenance files in the tree, and verifies the result from both source and post-unpack package.

## Hardware validation decision

No new physical hardware validation is claimed for this final package. The user stated that real hardware testing will be completed after the later full merge. Therefore, the final v2.0.0 MVP release relies on hermetic automated tests, release audit checks, and post-unpack verification, while documenting physical hardware validation as deferred.

## Invariants preserved

- External Player MVP flow remains in scope.
- M9702 / Chinoppo wake rewrite remains model-gated.
- Stock OPPO `#PON` / `#POW` pass-through remains preserved.
- TCL / Android TV ADB switching remains optional and non-fatal.
- Fake OPPO server tests remain hermetic.
- Kodi stub import tests remain present.
- `#SIS`, `#PGU`, and `#PGD` remain forbidden.
- 92% coverage gate and full v1.1.9 + v0.9.14 merge remain deferred.

# Version 2.0.0 Build 6 technical notes

Build 6 is a build-id update from the verified v2.0.0 final package. The add-on version is now `2.0.0.6`. Runtime MVP behavior is intentionally preserved.

## Design decision

The requested change was limited to the build id. Therefore, this build updates release identity, audit expectations, Build 6 notes, and Build 6 manifest evidence without expanding feature scope.

## Invariants preserved

- M9702 / Chinoppo `#PON` and `#POW` still resolve to `#EJT`.
- Stock OPPO `#PON` and `#POW` remain unchanged.
- The command map remains at 76 canonical keys.
- `#SIS`, `#PGU`, and `#PGD` remain forbidden.
- Clean TCP disconnect remains distinct from playback stopped.
- TV switching remains optional and failure-safe.
- Reavon remains warning-only.

## Audit update

`tools/audit_release.py` now includes `BUILD_NOTES_v2.0.0_BUILD6.md` and `RELEASE_MANIFEST_v2.0.0_BUILD6.md` in the required package-evidence list. The expected add-on version for Build 6 verification is `2.0.0.6`.

---

# Version 2.0.0 Final technical notes

Version 2.0.0 final packages the verified Build 5 MVP release-candidate line as the final v2.0.0 artifact. This step is intentionally small: final version identity, final release evidence files, updated tests, and final audit requirements. Runtime MVP behavior is preserved rather than rewritten.

## Finalization design decision

The Build 5 source tree had already satisfied the MVP functional scope and reproducible audit posture. The final step therefore avoids feature expansion and focuses on release correctness: package version `2.0.0`, final notes/manifest, final compliance evidence, and post-unpack verification.

## Invariants preserved

- M9702 / Chinoppo `#PON` and `#POW` still resolve to `#EJT`.
- Stock OPPO `#PON` and `#POW` remain unchanged.
- The command map remains at 76 canonical keys.
- `#SIS`, `#PGU`, and `#PGD` remain forbidden.
- `HARDWARE_COMPAT` remains aligned with the hardware-model settings enum.
- Clean TCP disconnect remains distinct from playback stopped.
- TV switching remains optional and failure-safe.
- Reavon remains warning-only.

## Audit update

`tools/audit_release.py` now requires the final evidence files: `RELEASE_NOTES_v2.0.0.md`, `RELEASE_MANIFEST_v2.0.0.md`, `MVP_COMPLIANCE_MATRIX_v2.0.0.md`, and `HARDWARE_VALIDATION_v2.0.0.md`, in addition to the prior release evidence. The expected add-on version for final verification is `2.0.0`.

## Coverage status

The 92% coverage gate remains staged for a later post-MVP hardening milestone. The final release does not claim that gate is complete.

---

# Version 2.0.0 Build 5 technical notes

Build 5 adds a reproducible release-audit layer for the v2 MVP release-candidate line. The functional MVP behavior from Build 4 is intentionally preserved; this build focuses on making the package easier to validate after it has been unpacked.

## Release audit helper design

`tools/audit_release.py` is dependency-free and can run in a normal Python environment. It is intended for local AI handoff, CI smoke checks, and user-side artifact verification. The helper checks Python compilation, XML parsing, locale parity, settings-string coverage, OPPO command-map invariants, hardware enum parity, required release files, and expected add-on version.

## Why this belongs in the MVP line

The v2 handoff requires tests and audits before packaging. Build 5 turns that requirement into a reusable project tool instead of relying only on ad hoc shell commands from a single build session.

## Invariants preserved

- M9702 / Chinoppo `#PON` and `#POW` still resolve to `#EJT`.
- Stock OPPO `#PON` and `#POW` remain unchanged.
- The command map remains at 76 canonical keys.
- `#SIS`, `#PGU`, and `#PGD` remain forbidden.
- `HARDWARE_COMPAT` remains aligned with the hardware-model settings enum.
- Clean TCP disconnect remains distinct from a playback stop event.

## Coverage status

The final 92% coverage gate remains staged. Build 5 strengthens release audit reproducibility, but does not treat staged coverage as complete.

---

# Version 2.0.0 Build 4 technical notes

Build 4 is an MVP release-candidate hardening build. It records the user-provided manual hardware-validation result and fixes the Build 3 hidden-file packaging regression.

## Manual hardware validation as project input

For Build 4, the project state assumes that the latest build was tested on the real hardware path and no issues were found. This assumption is recorded in `HARDWARE_VALIDATION_v2.0.0_BUILD4.md`. The automated tests still remain hermetic and do not claim to reproduce the physical OPPO/M9702/TCL/Android TV environment.

## Packaging regression fixed

Build 3's packaged zip omitted `.coveragerc`. The CI scaffolding test expects this file, so a post-unpack test run failed even though the source workspace had passed. Build 4 restores `.coveragerc` to the source tree and packages it explicitly. This is a release-process fix, not a playback behavior change.

## MVP compliance matrix

`MVP_COMPLIANCE_MATRIX_v2.0.0_BUILD4.md` records each MVP requirement and its status. The matrix is intended for both local-AI continuation and human release review. It distinguishes completed MVP requirements from staged post-MVP hardening, especially the final 92% coverage gate.

## Coverage gate rationale

The historical `.coveragerc` target remains `fail_under = 85` so the development scaffold remains truthful. The workflow keeps coverage in report mode while Kodi-bound tests are expanded. The final roadmap target of 92% remains staged rather than falsely claimed.

## Added release-artifact tests

Build 4 adds tests that verify the add-on version, Build 4 notes, manual hardware-validation note, MVP matrix, README/reference/web-reference synchronization, and `.coveragerc` restoration.

---

# Version 2.0.0 Build 3 technical notes

Build 3 adds the test-only Kodi API stub foundation required by the v2 roadmap's Kodi-mocking and coverage phase. This is a staged hardening build: it improves the ability to test Kodi-bound code outside Kodi, but it does not falsely claim the final 92% coverage gate is complete.

## Kodi stub design

The local stubs live under `tests/_stubs/` and are loaded only by tests that explicitly prepend that directory to `sys.path`. They are not packaged as runtime Kodi replacements and are not inserted globally through `conftest.py`. This preserves two important test modes:

1. **No-Kodi mode:** existing tests can still verify import guards and fallback behavior when `xbmc`, `xbmcaddon`, `xbmcgui`, and `xbmcvfs` are absent.
2. **Stubbed-Kodi mode:** new tests can exercise Kodi-bound imports and UI/settings paths without a real Kodi installation.

The stubs are intentionally minimal and programmable:

- `xbmc.py` records logs, supports `getInfoLabel`, and provides basic `Player` / `Monitor` classes.
- `xbmcaddon.py` provides `Addon().getSetting()`, `setSetting()`, `getAddonInfo()`, and `getLocalizedString()`.
- `xbmcgui.py` provides a recording `Dialog` with programmable `yesno`, `select`, and `input` responses.
- `xbmcvfs.py` provides `translatePath`, `mkdirs`, `exists`, and a small text `File` wrapper.
- `xbmcplugin.py` and `xbmcdrm.py` provide minimal placeholders for future tests.

## Coverage-gate staging decision

The roadmap permits a documented staged path when the 92% coverage gate is not yet honest. Build 3 keeps `.coveragerc` visible and keeps CI producing a coverage report, but changes the CI workflow so coverage reporting does not fail the package while the Kodi-bound stubs are being expanded.

This is intentional. A hard 92% gate should be restored only after the stubbed tests actually include the main Kodi-bound surfaces such as:

- `default.py`,
- `service.py`,
- installer menu/dialog paths,
- wizard dialog paths,
- Kodi settings and file-system wrappers.

## Test coverage added

Build 3 adds tests for:

- importing every local Kodi stub module,
- programmable `xbmc` log/info-label/Player/Monitor behavior,
- programmable `xbmcaddon.Addon` settings/info/localized strings,
- recording and scripted `xbmcgui.Dialog` behavior,
- `xbmcvfs` path and file helpers,
- importing `resources.lib.installer` with stubs active,
- importing `default.py` and `service.py` with stubs active.

The key invariant is that stubs help test Kodi-bound code without making the entire suite dependent on those stubs.

---

# Version 2.0.0 Build 2 technical notes

Build 2 turns the first v2 package into a stronger MVP candidate by focusing on the exact MVP path: External Player flow, M9702/Chinoppo wake behavior, TCL/Android TV switching, hermetic tests, and safe cleanup.

## Wake-command design correction

Build 1 correctly restored M9702/Chinoppo `#PON` / `#POW` to `#EJT` wake handling, but the shared wake-command helper could also turn stock OPPO `#POW` into `#PON`. Build 2 fixes that by requiring `is_clone=True` before applying the hardware profile `wake_command`. The invariant is now:

```text
UDP-203 / UDP-205: #PON stays #PON and #POW stays #POW.
Chinoppo-style clones: #PON and #POW resolve to #EJT.
Unknown models: original command is preserved.
Reavon: warning-only; no command-map mutation.
```

The same clone-only rule is applied in both `oppo_remote.resolve_power_on_token()` and `oppo_control._resolve_hardware_wake_command()` so remote-key forwarding and configured start commands cannot drift.

## MVP Slice 3 TV switching design

`external_player.fast_start()` now uses deterministic TV-first startup for the MVP: attempt TV switch to the OPPO input, then start OPPO/external playback. This intentionally prioritizes correctness and predictable tests over parallel startup during the MVP hardening phase.

TV switching is controlled by `tv_switching_enabled`. When disabled, the switch path is a logged no-op. When enabled, TV/ADB errors are logged as non-fatal. This protects the MVP cleanup invariant: ADB failure must not prevent OPPO startup, OPPO stop commands, or removal of the `oppo203iso-active` sentinel.

`adb_control.switch_input()` now accepts an injected subprocess-compatible runner through the `_adb_runner` setting. Tests use that seam to verify command construction without requiring a real TV or ADB binary.

> **Naming note (2026-05-31):** `adb_control` was later moved to `resources/lib/tv/` and renamed `tv_adb_control` (parity with the `avr_` drivers). This build note keeps the original name; see [`docs/NAMING_CONVENTIONS.md`](docs/NAMING_CONVENTIONS.md).

## Verbose-push disconnect invariant

`oppo_tcp_client.OppoTcpClient` now separates explicit stop events from transport closure. `wait_for_stop()` returns `True` only after a real stop-like `@UPL` / `@UPW` line. Clean socket disconnect returns `False`, allowing the persistent reconnect loop to retry rather than misreporting playback as stopped.

## Fake OPPO server design

`tests/_support/fake_oppo_server.py` provides a loopback TCP server for hermetic tests. It binds only to `127.0.0.1`, uses an ephemeral port, records commands, returns configurable `@OK` / `@ER` responses, and can push `@UPL` / `@UPW` lines or close mid-stream. This covers MVP integration behavior without physical hardware.

## Test coverage added

Build 2 adds tests for:

- stock OPPO `#PON` / `#POW` pass-through,
- M9702/clone wake rewrite retained from Build 1,
- TV switch-to-OPPO before OPPO startup,
- TV switching disabled no-op path,
- ADB/TV failure non-fatal behavior,
- stop commands still running when switch-back fails,
- sentinel cleanup on External Player startup failure,
- ADB command construction through injected runner,
- fake OPPO loopback `@OK` and `@ER` behavior,
- `@UPL STOP` stop-event handling,
- clean TCP disconnect not being treated as stop,
- persistent reconnect attempts after mid-stream disconnect.


---

# Version 2.0.0 Build 1 technical notes

This build starts the v2 MVP-first branch from the verified v1.x baseline. The immediate design choice is to keep the installable tree conservative: preserve the working v1.x modules, expose the hardware model needed for OPPO/Chinoppo behavior, restore the canonical OPPO command map, and remove the older architecture-selection UI rows from the visible Kodi settings surface.

The MVP invariant for M9702/Chinoppo hardware is send-time wake resolution. When a configured command is `#PON` or `#POW`, the selected hardware profile is consulted. Stock OPPO models keep the original command; Chinoppo/M9702-style models resolve the wake action to `#EJT`; Reavon remains warning-only and does not receive automatic command-map mutation.

The default command map is now the canonical 76-key map. Discrete inputs use `#SRC`; page navigation uses `#PUP` and `#PDN`. The legacy `#SIS`, `#PGU`, and `#PGD` tokens are blocked by regression tests.

Deferred work remains explicit: complete TCL/Android TV HDMI hardening in the External Player flow, add fake OPPO loopback server tests, and add Kodi API stubs before raising the coverage gate.

---

# Referee Notes for the Oppo UDP-203 ISO External Player Add-on

This file documents the design references, implementation decisions, and expected control flow for the add-on. It is intended to be readable without opening the web references separately. A second file, `web-references.md`, lists the source links and the most relevant extracted facts.

## User goal

The target behavior is:

1. Kodi runs on a separate box.
2. ISO files and supported video disc folder entries in Kodi should launch an Oppo UDP-203 workflow instead of Kodi's internal player.
3. The TV should automatically switch from the Kodi HDMI input to the Oppo HDMI input when ISO playback starts.
4. The TV should switch back from the Oppo HDMI input to the Kodi HDMI input when playback ends.
5. The transition to the Oppo should have the least practical delay.
6. The Kodi remote should still be usable for disc-menu navigation while the TV is showing the Oppo input, provided the remote events still reach Kodi.

## High-level architecture

The add-on uses Kodi's external-player mechanism instead of trying to play the disc image or folder inside Kodi. The add-on generates a `playercorefactory.xml` snippet with a player named `Oppo203ISO` and routing rules for ISO images plus optional video disc folder structures:

## Version 2.1.0 Build 6 technical notes

Build 6 is the final pre-merge coverage-gate hardening step. The gate is raised to `fail_under = 99` after adding behavior-oriented tests for defensive branches that were still uncovered after Build 5.

The new tests intentionally use local fakes and Kodi stubs rather than physical hardware. They validate meaningful code paths such as no-Kodi import fallback behavior, AutoScript CIFS generation, discovery timeout cleanup, OPPO HTTP/parser helpers, manual-file wait-loop behavior, TCP-client cleanup, stock OPPO power pass-through, playercorefactory merge branches, and settings XML child-value fallback.

No v1.1.9 + v0.9.14 merge work is included in this build.


## Version 2.1.0 Build 7 technical notes

Build 7 is a narrow coverage-quality hardening pass. Build 6 already displayed `TOTAL 99%`, but the raw combined line+branch percentage was just below 99%. Build 7 adds behavior-oriented tests for remaining branches so the raw combined percentage rises above 99 while keeping the same `fail_under = 99` gate.

### Design constraints

- No full v1.1.9 + v0.9.14 merge work was started.
- Tests remain hermetic and use local fakes/stubs only.
- The additional tests validate behavior on defensive branches instead of executing lines without assertions.

### Areas covered

- AutoScript wizard no-mount branch.
- HTTP polling hold with non-dict OPPO status payloads.
- TCP QPL polling confirmation branch before final idle exit.
- Discovery apply path where the discovered UDP port is not TCP port 23.
- Experimental file-list diagnostic path insertion branch.
- OPPO response parsing and command filtering defensive branches.
- No-Kodi OPPO remote logging fallback.

## Version 2.1.0 Build 8 technical notes

Build 8 is another narrow coverage-quality hardening pass. It does not introduce new runtime features and does not start the full historical superset merge. The purpose is to improve the raw combined line+branch coverage behind the already enforced 99% gate.

The added tests cover real defensive and edge behavior rather than executing lines artificially:

- `external_player.py` as a `__main__` entrypoint using local fake OPPO/settings/TV modules.
- `intercept.py` blacklist iteration and whitelist handling.
- `logging_v116.py` rotation behavior when destination removal fails.
- `oppo_control.py` empty command execution, non-dict HTTP status containers, list/dict audio track shapes, explicit directory/file inference, and size parsing.
- `oppo_tcp_client.py` partial TCP buffers without a line separator.
- `playercorefactory_merge.py` snippets with missing players/rules sections.
- `preset_manager.py`, `settings_reader.py`, and `wizard.py` defensive parsing/full-mode branches.

The enforced project coverage gate remains `fail_under = 99`, while raw combined line+branch coverage improved to 99.44%.

## Version 2.2.0 Build 1 technical notes

Build 1 begins the post-coverage superset merge in a deliberately narrow slice. The selected merge item is the v0.9.14 model-change compatibility watcher because it is isolated, testable, and directly connected to hardware compatibility without requiring a large wizard or service rewrite.

### Design decision

The existing `wizard.py` remains the active v2 wizard. A new narrow `resources/lib/first_run_wizard.py` module restores the compatibility helper API names from the v0.9.14 line: `apply_compatibility_preset`, `reapply_preset_on_model_change`, `quick_start_required`, `autoscript_verbose_push_warning`, and `log_compatibility_warnings`. This avoids a large wizard replacement while preserving the helper surface needed by the service watcher and future merge slices.

### Service watcher behavior

`service.Monitor.onSettingsChanged()` now reloads settings and checks only the hardware model and jailbreak flag. If neither changed, it exits without side effects. If a relevant setting changed, it re-applies the compatibility preset and logs warnings using the restored helper API. Errors are swallowed and logged so Kodi settings changes cannot break playback or service lifetime.

### Compatibility invariants preserved

- Stock OPPO `#PON` / `#POW` behavior remains unchanged in send-time command handling.
- Chinoppo/M9702 clone preset uses `#EJT` wake plus `#PLA` start commands.
- Reavon remains warning-only and command maps are not mutated.
- AutoScript shell-handler warning is surfaced as a warning string only.
- The 99% coverage gate remains enforced.

### Deferred merge work

The broader superset merge remains deferred to later slices: full v0.9.14 wizard integration, service watcher expansion beyond this compatibility path, remaining unique v0.9.14 tests, and full documentation reconciliation.



## Version 2.2.0 Build 2 technical notes

Build 2 is the second gradual superset-merge slice. It intentionally ports v0.9.14 hardware-compatibility tests before adding larger runtime features. The goal is to make the merge safer by locking down known compatibility invariants around Chinoppo clone models, Reavon warning-only behavior, jailbreak payload selection, and warning helper behavior.

### Audit hardening discovered during Build 2

While preparing this slice, the package carried an incorrect XML declaration value while the add-on version attribute still reflected the prior `2.1.0.8` line. The previous release audit looked for a version substring rather than parsing the add-on version attribute. Build 2 corrects `addon.xml` and hardens the audit so the XML declaration must use `version="1.0"` and the parsed `<addon>` `version` attribute must exactly match the requested build version.

### v0.9.14 compatibility invariants locked down

- M9203 and M9205C are explicit Chinoppo-style clones.
- M9203/M9205C use `#EJT` wake behavior and the clone preset `#EJT
#PLA` / `tcp_commands` / `oppo_http_activate=false`.
- Reavon UBR-X100/X110/X200 remain warning-only and do not mutate OPPO command maps or start commands.
- Stock OPPO UDP-203/UDP-205 with jailbreak enabled may use `oppo_http_payload_mode=json_payload`.
- Jailbreak payload behavior does not stack onto Chinoppo clones or Reavon models.
- AutoScript shell-handler warning remains informational and mentions the `#SVM 2` verbose-push risk.

The 99% coverage gate remains enforced. No physical OPPO, TV, Kodi, or ADB hardware was tested in this build.


## Version 2.2.0 Build 3 technical notes

Build 3 ports another small part of the v0.9.14 behavior set: compatibility warnings must be logged for support traces even when the user changes relevant settings outside the wizard.

### Design decision

The service watcher now treats `oppo_autoscript_shell_handler` as a relevant compatibility setting. When it changes, the watcher collects compatibility warnings through a side-effect-free helper and logs them using the existing `[v0.9.14-warning]` marker.

### Affected modules

- `resources/lib/first_run_wizard.py`: added `collect_compatibility_warnings()`.
- `service.py`: tracks the AutoScript shell-handler flag and logs combined warning sets.
- `tests/test_superset_merge_build3.py`: locks down warning collection and service watcher behavior.

### Invariants

- Reavon remains warning-only.
- AutoScript warnings are support-log behavior, not a playback blocker.
- Existing External Player, wake rewrite, TV switching, fake-server tests, and 99% coverage gate remain intact.


## Version 2.2.0 Build 10 technical notes — Merge-compliance checkpoint

Build 10 introduces a formal merge-compliance matrix for the gradual v1.1.9 + v0.9.14 superset merge. The matrix separates completed automated coverage from remaining manual or later-slice work. The build also formalizes the verification process improvement discovered during Build 9: coverage runs use `python -m coverage run -m pytest -q -p no:ddtrace`, with each verification command recorded separately.

The build intentionally avoids broad wizard replacement, major service rewrites, Reavon command-map support, or hardware-dependent changes.


## Version 2.2.0 Build 11 technical notes — active wizard compatibility flags

Build 11 connects another small v0.9.14 behavior slice into the active v1.x wizard. The design intentionally avoids replacing the stable wizard. Instead, full mode now captures two compatibility booleans already present in settings: `oppo_jailbreak_enabled` and `oppo_autoscript_shell_handler`.

For stock OPPO selections, the jailbreak flag can trigger the existing compatibility preset behavior that sets `oppo_http_payload_mode=json_payload`. For Reavon selections, the wizard surfaces warnings but does not mutate OPPO commands. For Chinoppo selections, Build 11 preserves the existing explicit confirmation prompt before changing start commands, minimizing risk while the full merge remains in progress.

The verification workflow continues to run commands one at a time and uses `-p no:ddtrace` during coverage runs to avoid local coverage/pytest plugin timeout behavior.

## Version 2.2.0 Release 2.2.0 technical notes

Release 2.2.0 is a final software merge-compliance review rather than a broad feature build. The v1.1.9 + v0.9.14 superset merge has been advanced to a software merge-complete candidate state for the hermetically testable scope. The compliance matrix records each hardware-compatibility, wizard, service watcher, command-map, coverage, documentation, and reconstruction item explicitly.

The build intentionally does not claim real hardware validation. OPPO, Chinoppo/M9702, TCL/Android TV, Kodi runtime, and ADB hardware validation remain external/manual.

The improved verification process from Build 10 remains mandatory: run each verification command separately and disable the local ddtrace pytest plugin during coverage runs with `-p no:ddtrace`.

## Version 2.2.0 technical notes

The v2.2.0 package converts Build 12 from a build-id artifact into a clean release identity. No broad rewrite was performed. The main release decision is to treat the software merge as complete candidate status while keeping hardware validation external and pending.

The Build 10+ verification process is retained: run commands separately and disable the local `ddtrace` pytest plugin during coverage runs to avoid container timeout behavior.

## v2.5.3 Build 2 Technical Reference — Option 4 XML rules

Option 4 intentionally replaces broad all-disc XML routing with conservative tag-aware routing. The rule generator emits `filename=".*(4K|4k|UHD|uhd|2160p|2160P).*"` on each routed disc-style filetype rule. The only routed filetypes are `iso`, `bdmv`, and `mpls`; loose/raw video formats are excluded by omission.

This design prevents untagged Blu-ray/DVD/VCD rips, raw stream files, and normal videos from being handed off unintentionally. It also keeps the service-interception classifier as the authoritative precise mode for Kodi playback-start detection.

Known limitation: Kodi XML filename/path matching is platform-dependent for folder-based BDMV playback. If a platform does not expose the movie folder segment to the XML rule, service interception should be used for exact classifier behavior.

## v2.5.3 Build 3 Technical Reference — Version identity reconciliation

Build 3 resolves the Build 2 metadata mismatch where package artifacts used the v2.5.3 Build 2 identity but `addon.xml` still carried `2.5.2` for inherited audit compatibility. The reconciled runtime version is now `2.5.3` and release audit expectations require `2.5.3`.

This is a metadata/audit/documentation slice only. The Build 1 4K disc-style classifier and Build 2 tag-aware XML generation remain unchanged.



## v2.5.3 Build 4 technical note — playercorefactory merge hardening

Build 4 aligns `resources/lib/playercorefactory_merge.py` with the Option 4 conservative XML policy. Helper-generated snippets no longer use the old broad `iso|bdmv|m2ts` rule. They emit separate `iso`, `bdmv`, and `mpls` rules that each require the `4K|4k|UHD|uhd|2160p|2160P` filename/path tag pattern. The merge helper backs up existing files before write, deduplicates players and rules by name, validates the written XML, and attempts to restore the original file on write or validation failure.


## v2.5.3 Build 5 technical note — hardware-validation readiness export

Build 5 adds `resources/lib/hardware_validation_readiness.py`, a read-only support helper that combines the existing diagnostic summary with NAS/AutoScript capability gating and a fixed tester checklist. The output is intended to make hardware test evidence consistent across OPPO UDP-203/205, Chinoppo/M9702-family devices, Kodi platforms, NAS path mappings, Option 4 XML routing, and TV/ADB switching scenarios.

The helper deliberately separates readiness from validation. It always reports `hardware_validation_claimed: false` and `safe_to_claim_hardware_pass: false` because only user-provided real-device results can establish hardware validation.

The installer menu export writes a text file only. It does not modify settings, push AutoScript files, contact OPPO hardware, switch TV inputs, or start playback.

## v2.5.3 Build 6 technical note — pre-hardware release-candidate freeze

Build 6 is a packaging/evidence freeze. The technical baseline is intentionally unchanged from Build 5: precise Python service interception remains the most exact route, Option 4 XML routing remains conservative and naming-driven, XML merge/rollback behavior remains idempotent, and the hardware-validation readiness export remains available for testers.

The main engineering purpose is to produce a stable candidate for physical testing while keeping the installable ZIP runtime-only and preserving a complete AI handoff/reconstruction record outside the runtime package.

## v2.9.0 release technical note

Version 2.9.0 is a release-identity rebuild from the v2.5.3 Build 6 software candidate. Runtime behavior is intentionally unchanged. The release keeps the Build 1 service classifier, Build 2 Option 4 conservative XML routing, Build 4 XML merge/rollback safety, and Build 5 hardware-readiness reporting.

The release continues to require naming discipline for XML mode: visible path or filename tags must include `4K`, `UHD`, or `2160p`, and XML routing remains limited to disc-style `iso`, `bdmv`, and `mpls` entries. XML mode cannot inspect metadata, NFO files, stream resolution, or ISO internals.

## v2.9.1 Build 1 technical note

v2.9.1 Build 1 is a UX clarity build for the first-run wizard. It updates the Kodi startup auto-power prompt from a short power-on question to explicit optional wording:

```text
Kodi startup auto-power
Do you want Kodi to automatically power on the OPPO/compatible player when Kodi starts? Choose No if you prefer to keep the player off until playback starts or you power it on manually.
```

The underlying setting key remains `kodi_startup_power_on`. Choosing No writes `false` and skips the Wake-on-LAN/delay/retry follow-up prompts. Choosing Yes preserves the existing advanced follow-up behavior. No OPPO command, startup power implementation, playercorefactory.xml routing, service interception, NAS adapter, or hardware-control logic changed.

## v2.9.1 Build 2 technical note

v2.9.1 Build 2 introduces `resources/lib/disc_classification.py` as the shared implementation for tagged 4K/UHD/2160p disc-style classification. The module intentionally preserves the historical substring tag detection and disc-style rules so the build remains behavior-preserving. `intercept.py` now delegates its 4K disc-source wrappers to the shared helper, and the installer/playercorefactory merge helpers import the same XML filename pattern and disc/loose-video filetype constants.

`resources/lib/constants.py` begins the safe constants cleanup by documenting protected invariants such as `OPPO_COMMAND_MAP_SIZE = 76` and `MIN_COVERAGE_PERCENT = 99`. The actual OPPO command-map data remains in its historical location until the dedicated command-map migration build.

## v2.9.1 Build 3 technical note — command-map externalization

The canonical OPPO command map now lives in `resources/data/oppo_command_map.json`. `resources/lib/command_map.py` provides a validated loader and immutable `CommandMap` wrapper that enforces the 76-key invariant and rejects forbidden command tokens before the map is used.

For compatibility, `settings_reader.DEFAULTS["oppo_remote_command_map"]` remains a JSON string generated from the externalized map, and `oppo_remote.DEFAULT_COMMAND_MAP` loads through the validated helper. This preserves user override merging and existing runtime behavior.


## v2.9.1 Build 4 — Dynamic audit evidence discovery

Version 2.9.1 Build 4 adds manifest-based release-evidence discovery to `tools/audit_release.py`. The audit now discovers `release-evidence/*/MANIFEST.txt`, requires each manifest file, and requires every safe root-relative evidence file listed in those manifests. The legacy hard-coded evidence list remains active as a transition fallback so historical checks remain stable while future builds can migrate to manifest-owned evidence.

No playback behavior, OPPO command-map behavior, service interception, XML routing, NAS playback, startup auto-power, or hardware-control behavior changed. Hardware validation is not claimed for this build.

## v2.9.1 Build 5 — Version single source of truth

Build 5 adds `resources/lib/version.py` as the Python source of truth for add-on release identity and `tools/sync_version.py` for checking or synchronizing `addon.xml`. The release audit now verifies that `addon.xml`, `version.py`, and `--expected-version` agree. Runtime playback/control behavior is unchanged, and hardware validation is not claimed.


## v2.9.1 Build 6 — Build/release automation scripts

Build 6 introduces portable shell wrappers for the existing verification and packaging workflow. The scripts keep the release process local: `scripts/verify.sh` runs py_compile, version consistency, pytest with `-p no:ddtrace`, unittest, coverage with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, and the release audit. `scripts/package_release.sh` checks version consistency, calls `tools/package_installable_zip.py`, writes SHA256 checksums, and creates a dev-source ZIP. Runtime behavior is unchanged.

## v2.9.1 Build 7 technical notes — allowlist runtime packaging

Build 7 refactors `tools/package_installable_zip.py` from prefix/denylist-style runtime filtering to an explicit allowlist. The allowlist is intentionally narrow: root runtime files, optional root runtime assets, and `resources/**`. This makes unknown future top-level development files excluded by default and reduces the risk of accidentally shipping tests, tools, scripts, release evidence, or handoff artifacts in the Kodi runtime ZIP.

The Build 7 change is packaging-only. Runtime playback/control behavior is unchanged.

## v2.9.1 Build 8 technical notes — settings exception narrowing phase 1

Build 8 isolates legacy defensive string conversion in `_setting_text()` and narrows low-risk numeric/XML parsing handlers to specific exception classes. This begins recommendation #6 without introducing a schema dependency or changing runtime behavior.


## v2.9.1 Build 9 — Settings schema / typed validation, phase 2

Build 9 adds a dependency-free typed settings schema in `resources/lib/settings_schema.py`. The schema is advisory and non-mutating: existing `Settings` getters still provide the same safe fallback behavior, while `schema_issues()` and `typed_values()` expose structured validation for diagnostics and future hardening. No playback, OPPO command-map, XML routing, NAS adapter, startup auto-power, or hardware-control behavior changed.

## v2.9.1 Build 10 — Audit reporter refactor

The release audit now exposes typed audit checks through `collect_audit_checks()` and renders output through dedicated text/JSON reporter classes. This preserves compatibility for older tests and local AI workflows that still call `run_audit()` and expect dictionaries, while making future reporter formats easier to add.

## v2.9.1 Build 11 — Diagnostic logging fallback refactor

Build 11 introduces `KodiLogHandler` and a structured fallback logger in `resources/lib/diagnostic_logging.py`. `log_to_xbmc()` still returns the formatted message and preserves `[OPPO203][CATEGORY]` support prefixes. When Kodi is unavailable, the fallback uses a Python `logging.StreamHandler` instead of direct per-call `print()` behavior.

The change is intentionally internal and non-invasive: playback, OPPO commands, startup auto-power, XML routing, NAS playback, and runtime packaging behavior are unchanged.




## v2.9.10 Build 3 technical note — capability gates

Build 3 adds explicit read-only capability helpers for stock OPPO, Chinoppo-style clone-family hardware, experimental clones, and OPPO-like successors. Automatic OPPO command-map behavior is allowed only for stock OPPO and clone-family profiles. Warning-only successors such as Reavon and Magnetar are excluded from clone-safe wake and NAS direct-playback support until real device validation is recorded.



## v2.9.10 Build 4 — Player wizard wording and readiness updates

Build 4 updates player-facing guidance for the v2.9.10 hardware taxonomy. The wizard and readiness report now explain stock OPPO behavior, Chinoppo-style clone behavior, experimental clone readiness gates, and warning-only OPPO-like successor behavior for Reavon and Magnetar. NAS/direct playback remains a readiness gate requiring AutoScript or equivalent local NAS mount support on the player.

No playback routing, OPPO command-map payloads, service interception, Option 4 XML routing, NAS adapter behavior, startup auto-power behavior, TV switching behavior, AVR sequencing, or hardware-control behavior changed. Hardware validation is not claimed.

## v2.9.1 Build 12 technical note — docs metadata/rendering pipeline

Build 12 introduces `docs/sources.yaml` and `tools/render_docs.py` as a transition toward shared documentation metadata. The tool intentionally parses a tiny project-owned YAML subset instead of adding PyYAML/Jinja dependencies. It appends or replaces only the generated metadata block between `
## v2.9.10 Build 6 — Android / Google TV preset pack

Version 2.9.10 Build 6: Android / Google TV preset pack.

Build 6 extends `resources/lib/tv_presets.py` with nine Android / Google TV ADB software presets: `tcl_android_tv`, `sony_android_tv`, `hisense_android_tv`, `philips_android_tv`, `xiaomi_android_tv`, `sharp_android_tv`, `skyworth_android_tv`, `haier_android_tv`, and `generic_android_tv`.

The implementation is intentionally metadata-only. Each Android / Google TV preset uses the preserved `adb` backend, marks command fields as editable, keeps hardware validation required, and records that No universal ADB HDMI command is claimed. Hardware validation is not claimed. Runtime dispatch remains in the existing `tv_control.switch_to_oppo(settings)` and `tv_control.switch_to_kodi(settings)` flow, so ADB failures remain non-fatal in the established playback path.


## Version 2.9.10 Build 9B — SmartThings experimental request helper and fake API tests

The Build 9B SmartThings slice registers the `smartthings` backend as experimental metadata only. It records acknowledgement, token, device ID, and input ID placeholders; token values must be redacted in support paths; and live SmartThings requests are intentionally disabled for this build.


## Version 2.9.10 Build 12 — Denon / Marantz AVR driver

Build 12 adds guarded Denon/Marantz Telnet-style AVR command support behind the disabled-by-default AVR framework from Build 11. The driver supports `PWON` for power on, `SI<input>` for input selection, and query helpers for `PW?` and `SI?` where supported. Each command opens and closes a socket, uses a short timeout, and returns a non-fatal `AvrResult` on timeout, network failure, invalid input, or unsupported action.

AVR control remains disabled by default, AVR power-off remains disabled by default, volume automation remains disabled by default, and AVR playback sequencing is not hooked in this build. Hardware validation is not claimed.


## Version 2.9.10 Build 13 — Yamaha MusicCast / YXC AVR driver

Build 13 adds guarded Yamaha MusicCast/YXC HTTP command support behind the disabled-by-default AVR framework. The driver uses HTTP GET helpers for `/YamahaExtendedControl/v1/main/setPower?power=on`, `/YamahaExtendedControl/v1/main/setInput?input=<input>`, and `/YamahaExtendedControl/v1/main/getStatus`, parses JSON `response_code`, and returns non-fatal `AvrResult` objects for non-zero response codes, invalid JSON, timeouts, and network failures.

AVR control remains disabled by default, AVR power-off remains disabled by default, volume automation remains disabled by default, and AVR playback sequencing is not hooked in this build. Denon / Marantz AVR driver behavior from Build 12 remains preserved. Hardware validation is not claimed.



## Version 2.9.10 Build 14 — Onkyo / Integra / Pioneer eISCP AVR driver

Build 14 adds guarded Onkyo / Integra / Pioneer eISCP command support behind the disabled-by-default AVR framework. The driver uses TCP port `60128`, eISCP frame magic `ISCP`, power-on payload `!1PWR01`, and input-select payloads `!1SLIxx`. It builds valid eISCP frames, opens and closes a socket per command, handles malformed response frames safely, returns non-fatal `AvrResult` objects for timeout/network/error/malformed-response paths, keeps Pioneer marked experimental/unverified, and does not hook AVR into playback sequencing.

AVR remains disabled by default. AVR power-off and volume automation remain disabled by default. Hardware validation is not claimed.


## Version 2.9.10 Build 15B — Sony AVR experimental request helper

Build 15B adds a Sony Audio Control API experimental request helper behind the disabled-by-default AVR framework. It adds Sony AVR preset metadata, explicit experimental acknowledgement gating, settings placeholders, validation helpers, sanitized diagnostics metadata, and regression tests. It uses guarded fakeable JSON POST helpers only after explicit acknowledgement, refuses Sony AVR execution unless experimental acknowledgement is enabled, never logs or exports Sony PSKs, passwords, credentials, tokens, or secrets, does not hook AVR into playback sequencing, and does not claim hardware validation.

Balanced Gate verification is used for this feature build. Full legacy pytest, full unittest discovery, and full post-unpack coverage remain deferred to Build 18 regression/audit packaging.


## Version 2.9.10 Build 16 — AVR wizard, diagnostics, and safety UI

Build 16 adds AVR setup UI helpers, query-only AVR test actions, explicit user-action gates for power/input tests, sanitized AVR diagnostic export, and safety wording. AVR support remains disabled by default, AVR power-off and volume automation remain disabled by default, no AVR playback sequencing hook is added, diagnostics sanitize credentials and state `hardware_validation_claimed=false`, and hardware validation is not claimed.

<!-- BEGIN GENERATED DOCS METADATA -->
### Generated documentation metadata — v2.9.14 Final

- Target document: `reference.md`
- Cleanup scope: Six-option playback architecture, richer session status, and robustness hardening
- Runtime behavior changed: `true`
- Hardware validation claimed: `false`
- Source recommendation: v2.9.14 six-option playback architecture, richer session status, and robustness roadmap
- Managed documents: `README.md`, `reference.md`, `web-references.md`

Protected behavior preserved:
- 4K/UHD/2160p disc-style interception only
- loose/raw video files stay with Kodi
- Option 4 conservative playercorefactory.xml behavior
- canonical 76-key OPPO command map
- no forbidden OPPO command tokens #SIS #PGU #PGD
- Reavon warning-only behavior
- Chinoppo/M9702 wake rewrite behavior
- stock OPPO pass-through behavior
- Kodi startup auto-power guard behavior
- NAS adapter behavior
- runtime-only installable ZIP policy
<!-- END GENERATED DOCS METADATA -->
`.

This build does not replace the historical handoff or hand-written references. It only creates a repeatable checkable metadata block for README/reference/web-reference consistency.


## v2.9.1 Build 13 technical note — type hints and non-blocking mypy baseline

Build 13 starts gradual typing by adding `tools/type_check.py`, `mypy.ini`, and selected public helper annotations. The wrapper skips cleanly when mypy is not installed and can be made strict with `--strict-exit` for local development. Runtime Kodi behavior remains unchanged.

## v2.9.1 Build 14 technical note — test naming/layout transition

Build 14 defines the future test layout without moving historical tests. `tools/test_layout.py` accepts future paths such as `tests/v2_9_1/build14/test_example.py`, inherited flat tests such as `tests/test_all.py`, and support paths under `tests/_support` or `tests/_stubs`.

## v2.9.1 Build 15 technical note — Babel/gettext extraction transition

Build 15 creates an i18n extraction facade in `tools/i18n_extract.py`. The facade supports `--backend auto`, `--backend legacy`, and `--backend babel`; Build 15 verification uses `--check` so no generated `strings.pot` is written during normal verification. Because this add-on uses Kodi numeric localization ids as gettext `msgctxt` values, the facade preserves `tools/make_pot.py` as the fallback and renderer compatibility source for this build.

`babel.cfg` is included for a Babel/gettext-style workflow, but Babel remains optional and development-only. Runtime Kodi packaging remains allowlist-only and excludes all extraction tooling.


## v2.9.1 Build 16 technical note — i18n extraction legacy alias hardening

Build 16 makes the extraction fallback retirement decision explicit: `tools/make_pot.py` is **not removed in Build 16**. It remains a legacy compatibility alias with its deterministic parser/renderer contract preserved. New build automation should call `tools/i18n_extract.py`, which continues to validate that facade extraction and the legacy parser agree.

The legacy alias policy is intentionally conservative so old calls to `python3 tools/make_pot.py` remain safe while documentation, verification, and new tests point to the facade as the primary entrypoint.


## v2.9.10 Build 1 — Unified hardware registry foundation

Build 1 starts the v2.9.10 Unified Hardware Ecosystem Expansion by adding a side-effect-free hardware registry foundation for player, TV, and AVR role families. The new registry is documentation/test-oriented in this build and does not change playback routing, OPPO command dispatch, service interception, Option 4 XML routing, NAS behavior, startup auto-power behavior, existing TV switching behavior, or AVR sequencing.

Hardware validation is not performed or claimed.


## Version 2.9.10 Build 2 — OPPO clone taxonomy and aliases

Build 2 expands the software taxonomy for OPPO-compatible player profiles without changing playback routing or OPPO command-map payloads. It adds M9200, M9205, CineUltra V203, CineUltra V204, and Magnetar UDP900 identifiers, plus M9702 V1/V2/V3 and related spelling aliases. Clone-family additions use the existing clone-safe wake classification, while Magnetar UDP900 is warning-only / unverified by default.

No real hardware validation is claimed for the new identifiers. The runtime ZIP remains allowlist-only and development evidence remains outside the installable package.

## v2.9.10 Build 5 — TV backend registry and preset foundation

Build 5 creates `resources/lib/tv_backends.py` and `resources/lib/tv_presets.py` as the foundation for the v2.9.10 TV expansion phase. The backend registry is deliberately metadata-first: it describes existing TV switching backends and the setting keys they already use, but it does not add network calls or alter the established public TV control functions.

The TV preset registry is also software-only in this build. It gives later Android TV, Roku ECP, command preset, and diagnostic builds a stable place to register presets while keeping existing command fields editable and preserving non-fatal TV switching behavior. Hardware validation remains tester-owned and is not claimed by this software build.

## Version 2.9.10 Build 9B — SmartThings experimental request helper and fake API tests

The Build 9B SmartThings slice registers the `smartthings` backend as experimental metadata only. It records acknowledgement, token, device ID, and input ID placeholders; token values must be redacted in support paths; and live SmartThings requests are intentionally disabled for this build.

<!-- BEGIN GENERATED DOCS METADATA -->
<!-- END GENERATED DOCS METADATA -->

## v2.9.10 Build 8 — Roku TV ECP backend

Version 2.9.10 Build 8: Roku TV ECP backend.

Build 7 adds `resources/lib/roku_ecp_control.py` and the `roku_ecp` TV backend. The backend sends local HTTP POST requests to `/keypress/<key>` using default port `8060`. Roku keys are allowlisted before URL construction to prevent path or query injection. Supported software-preset key examples include `InputHDMI1` and `InputHDMI2`; unsupported or unsafe values fail before any network call.

> **Naming note (2026-05-31):** `roku_ecp_control` was later moved to `resources/lib/tv/` and renamed `tv_roku_ecp_control`. This build note keeps the original name; see [`docs/NAMING_CONVENTIONS.md`](docs/NAMING_CONVENTIONS.md).

Build 7 also extends `resources/lib/tv_presets.py` with software-only Roku TV presets: `roku_tv`, `tcl_roku_tv`, `hisense_roku_tv`, and `generic_roku_tv`. Hardware validation is not claimed.

Build 7 implementation note: Roku TV ECP uses HTTP POST to /keypress/<key> with allowlisted input keys.

## Version 2.9.10 Build 8 — Command TV preset polish

The Build 8 command preset slice adds explicit preset records for `lg_webos_command`, `samsung_command`, `panasonic_custom_command`, `vizio_custom_command`, and `generic_custom_command`. These presets are metadata and documentation helpers only; the existing `lg_command`, `samsung_command`, and `custom_command` backends remain editable and user-owned.


## Version 2.9.10 Build 10 — TV diagnostics and dry-run validator

Build 10 adds `resources/lib/tv_diagnostics.py` for selected-backend validation, network-free dry-run reports, explicit switch test helpers, and sanitized diagnostic export. Reports include `hardware_validation_claimed=false` and redact SmartThings/Sony secrets and command output.

## Version 2.9.10 Build 11 — AVR framework and settings skeleton

Build 11 creates the generic AVR framework used by later v2.9.10 AVR builds. Runtime files include metadata-only AVR preset lookup, typed result/validation objects, disabled-by-default settings, and a no-op/factory path for diagnostics. The enabled-but-incomplete path reports missing configuration safely; the enabled metadata-only path still refuses to execute brand commands until future driver builds add guarded implementations. No OPPO playback routing, TV diagnostics, SmartThings guardrails, Roku ECP behavior, Android TV ADB presets, service interception, playercorefactory.xml behavior, NAS/AutoScript behavior, startup auto-power behavior, or runtime packaging semantics changed.


## Version 2.9.10 Build 17 — Unified TV + AVR playback sequencing

Build 17 safely hooks optional TV and AVR pre/post sequencing into the external-player flow. AVR sequencing runs only for eligible OPPO/external-player handoff, the AVR disabled path is a no-op, TV and AVR failures remain non-fatal, optional AVR restore runs only when enabled, and existing TV restore continues to work. Startup power, service interception, playercorefactory.xml routing, NAS/AutoScript behavior, loose/raw file exclusion, OPPO command-map payloads, runtime ZIP policy, the 99% coverage gate, and the no-hardware-validation-claim posture remain preserved.

### Generated documentation metadata — v2.9.10 Build 17

The generated docs metadata block above records Build 17 as the active v2.9.10 software build. Build 17 uses the shortened Balanced Gate verification strategy and defers full legacy pytest, full unittest discovery, and full post-unpack coverage to Build 18 Full Release Gate.

## Version 2.9.10 Build 18 — Regression, audit, and packaging candidate

Build 18 is the Full Release Gate regression/audit candidate for the v2.9.10 software line. It intentionally avoids new hardware features and verifies that Build 17 unified TV + AVR playback sequencing remains stable under full source, test, coverage, audit, post-unpack, and runtime ZIP checks.

The software support matrix continues to separate implemented software paths from real hardware validation. Hardware validation is not claimed unless separate real tester results are supplied.

## Version 2.9.10 Final — Software-verified release packaging

Final v2.9.10 preserves the Build 18 regression/audit candidate and packages the final runtime ZIP, dev-source ZIP, artifact bundle, and SHA256 checksum. The runtime ZIP remains runtime-only and excludes tests, tools, scripts, docs, release evidence, reports, handoff files, caches, and compiled Python files.

Hardware validation remains not performed and not claimed. Software support and real hardware-validated support remain separate in the support matrix.
