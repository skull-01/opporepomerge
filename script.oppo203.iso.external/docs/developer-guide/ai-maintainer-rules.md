# Developer Guide — AI Maintainer Rules

These rules are mandatory for future AI agents working on this project.

## Always preserve the baseline

For GitHub readiness, preserve v2.9.10 Final runtime behavior unless the user explicitly authorizes a narrow behavior change.

## Always produce handoff files

Every build must produce an AI handoff file that another AI can use to resume work.

Minimum handoff sections:

- current status
- baseline package
- scope completed
- files changed
- files added
- validation performed
- validation not performed
- known issues/limitations
- packaging notes
- historical reconstruction entry
- next-build resume prompt

## Always update historical reconstruction

Every build must include a historical reconstruction entry with enough detail to rebuild the work.

Required YAML keys:

```yaml
build_id:
baseline:
scope:
planned_success_rate:
actual_outcome:
hardware_validation:
runtime_behavior_changed:
```

## Never claim hardware validation without evidence

Software tests, mocks, package audits, and CI do not prove real hardware behavior.

Allowed status:

```text
hardware_validation: not_performed_not_claimed
```

Only change this when real tester evidence is supplied and recorded.

## Keep packages clean

Runtime ZIP must remain runtime-only. Dev-source and artifact bundles may contain docs, tests, tools, and evidence.

## Record limitations honestly

If a command times out, say it timed out. If a tool is unavailable, say it is unavailable. Do not convert partial evidence into a full pass.

## Prefer small builds

Split large work into small builds to prevent timeout and make review easy.

## Protect secrets

Never add diagnostics that reveal credentials, tokens, PSKs, or local private data.

## Change discipline

Before changing code, identify whether the change is:

- documentation-only
- tooling-only
- test-only
- packaging-only
- runtime behavior

Runtime behavior changes require more evidence and should not be mixed with documentation/tooling work.
