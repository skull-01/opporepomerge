# Build Notes — v2.5.3 Build 1

## Objective

Implement the first software slice for 4K UHD disc-style interception from the v2.5.2 Build 8 baseline.

Build 1 is intentionally limited to the Python classifier and service-interception integration. It does not implement the selected Option 4 playercorefactory.xml rule generation, wizard naming-convention warning, or final packaging hardening; those remain assigned to v2.5.3 Build 2.

## User-approved interception policy

Intercept only when all of the following are true:

1. The path contains one of the approved 4K tags: `4K`, `UHD`, or `2160p`.
2. The source is disc-style: `.iso`, `.bdmv` navigation, or `BDMV/PLAYLIST/*.mpls`.
3. The source is not a loose/raw video file.

Always exclude these loose/raw video extensions even when their names contain 4K tags:

`.mkv`, `.mp4`, `.m4v`, `.mov`, `.mpg`, `.mpeg`, `.avi`, `.wmv`, `.flv`, `.webm`, `.ts`, `.m2ts`, `.mts`, `.m2t`, `.vob`, `.ogm`, `.ogv`, `.divx`, `.xvid`, `.3gp`, `.3g2`, `.f4v`, `.rm`, `.rmvb`, `.asf`.

## Files changed

- `resources/lib/intercept.py`
  - Added `should_intercept_4k_disc_source(path)`.
  - Added 4K tag constants, loose/raw video exclusion constants, and narrow disc-style helpers.
  - Preserved historical `classify`, `is_disc_image`, and `should_intercept` behavior.
- `service.py`
  - Added dynamic `_should_intercept_4k_disc_source(path)` wrapper.
  - Replaced broad service `_is_disc_path(path)` gate in `_handle_started()` with the centralized 4K disc-style classifier.
  - Updated log wording to distinguish tagged 4K disc-style interception from default Kodi playback.
- `tests/test_v253_build1_4k_disc_interception.py`
  - Added targeted tests for tagged ISO, BDMV navigation, untagged discs, excluded loose/raw videos, non-disc paths, and service wrapper integration.
- `tools/audit_release.py`
  - Added v2.5.2 Build 2 evidence to the preserved audit list to restore compatibility with the existing packaging-cleanup audit test.
  - Added v2.5.3 Build 1 evidence files to the audit list.

## Explicitly deferred to Build 2

- Conservative tag-aware playercorefactory.xml rules, Option 4.
- Wizard naming-convention warning.
- README/user documentation updates beyond this handoff/build evidence.
- Final runtime installable ZIP packaging and artifact bundle hardening.

## Hardware status

Software-tested only. No physical OPPO, Chinoppo/M9702, Kodi installation, NAS, or TV switching hardware was validated in this build.

