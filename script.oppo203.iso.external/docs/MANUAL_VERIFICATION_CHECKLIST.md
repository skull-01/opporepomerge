# Manual Verification Checklist

**Purpose:** the operator's queue of "agent claimed done; operator must verify before
closing the issue." Per the **only-operator-closes-issues** norm, agents never call
`gh issue close` and never write `Closes/Fixes/Resolves #N` — instead they comment the
implementing SHA(s) on the issue and append a row here.

## How to use

- **Agents:** when work seems done, append an entry under the right phase. Include the
  issue number, the implementing SHA(s), and the exact steps the operator should run to
  confirm.
- **Operator:** work the list top-down. When a row passes Phase C, close the GitHub
  issue and check the row off (or strike it out and move to a "Verified" archive section
  at the bottom).

## Phase definitions

- **Phase A — pre-merge.** PR is open. Operator verifies the diff makes sense, CI is
  green, and the change does what the issue says. Block: anything that should be fixed in
  the PR before merge.
- **Phase B — post-merge sanity.** PR is merged to `main`. Operator confirms `main` still
  builds + tests, nothing visible is broken. Block: a regression caught here typically
  means a hotfix or revert, not a slow re-verification cycle.
- **Phase C — operator end-to-end verify.** Operator runs the change in the real
  environment (Kodi on the actual box, the configurator on the actual Windows host,
  against the actual hardware chain). This is the **only** step that authorizes closing
  the issue.

---

## Phase A — pre-merge

- **[#41](https://github.com/skull-01/script.oppo203.iso.external/issues/41)
  (ENH-: configurator owns add-on configuration — policy doc, part A)** —
  branch `claude/config-owner-policy-a3k7m2nq`. Docs-only PR adding a
  `## Configuration is owned by the configurator` section to
  [`AGENTS.md`](../AGENTS.md) and a `## Configuration ownership` section to
  [`CONTRIBUTING.md`](../CONTRIBUTING.md). Read both new sections and confirm:
  (1) the policy statement matches your intent ("configurator owns persistent
  config; add-on read-mostly"); (2) the three allowed exceptions are correct
  (per-session toggles, the #42 settings menu carve-out, diagnostic exports);
  (3) the "not allowed" list is correct (new persistent-setting categories,
  new first-run dialogs, add-on side writers for `playercorefactory.xml` /
  keymap / NAS creds). Parts B (in-add-on guidance hint) and C
  (settings-file ownership marker) are out of scope for this PR and wait
  until [#40](https://github.com/skull-01/script.oppo203.iso.external/pull/40)
  merges. No code paths exercised — docs-only.

## Phase B — post-merge sanity

_(none queued)_

## Phase C — operator end-to-end verify

_(none queued)_

---

## Verified (archive)

_Move rows here after Phase C passes and the issue is closed. Newest at the top._

_(empty)_
