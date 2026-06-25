# Archived GitHub metadata

Snapshot (2026-06-25) of **Issues, Pull Requests, and Releases** from the source repositories that were consolidated into this monorepo. The git history, branches, and tags of those projects already live in this repo's subdirectories — but GitHub Issues/PRs/Releases are *not* part of git, so they are captured here so the original standalone repositories can be retired without losing their discussion and release notes.

Each repo folder holds lossless JSON (`issues.json`, `pulls.json`, `releases.json`, and per-thread `comments/*.json`) plus rendered Markdown for browsing.

| Source repo | Issues | PRs | Releases | Issue comments | PR comments | Rendered |
|---|---|---|---|---|---|---|
| [`script.oppo203.iso.external/`](script.oppo203.iso.external/) | 119 | 253 | 42 | 201 | 66 | [Issues](script.oppo203.iso.external/ISSUES.md) · [Pulls](script.oppo203.iso.external/PULLS.md) · [Releases](script.oppo203.iso.external/RELEASES.md) |
| [`OppoKodiBridge/`](OppoKodiBridge/) | 0 | 0 | 8 | — | — | [Releases](OppoKodiBridge/RELEASES.md) |
| [`OppoKodiBridge-v3/`](OppoKodiBridge-v3/) | 0 | 1 | 1 | — | — | [Pulls](OppoKodiBridge-v3/PULLS.md) · [Releases](OppoKodiBridge-v3/RELEASES.md) |
| **Total** | **119** | **254** | **51** | **201** | **66** | |

## Scope / fidelity notes
- **Issue comment threads captured** — 201 comments across every issue that had any.
- **PR comments captured** — both conversation comments and inline review comments, where present, are stored in `comments/pr-<N>-conversation.json` / `pr-<N>-review.json` and inlined into `PULLS.md`.
- **Releases had no binary assets**; the release notes are the unique content.
- `CEC-Control-Experiment` had no issues/PRs/releases (git-only), so it has no folder here.
- This archive was verified against the live GitHub API (counts + verbatim content spot-checks) before commit.
