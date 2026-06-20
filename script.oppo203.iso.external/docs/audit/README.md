# docs/audit/

Ground-truth audits of merged `area:addon` work whose issues are still **open** pending the
operator's hardware **Phase C**. Each audit confirms the fix in the current code (`file:line` + a
passing test) and gives the exact on-device steps to verify and close — so the hardware session is
a checklist, not a re-investigation.

- [`addon_robustness_audit.md`](addon_robustness_audit.md) — robustness bugs #111 / #112 / #114 / #115 / #116 / #117 / #123 (merged via #129–#133).
- [`addon_svm3_audit.md`](addon_svm3_audit.md) — SVM3 four-option ENHs #150 / #151 / #152 + verify-played #113 (merged via #143 / #144 / #145).

**Scope + signature.** Documentation only — no runtime change. "Confirmed fixed in code" means the
change is on `main` and pinned by a passing test; it is **not** a hardware-validation claim. The
Phase-C steps in each file are what validate the real-device behavior, and only the operator closes
the issues. Linked from [`../MANUAL_VERIFICATION_CHECKLIST.md`](../MANUAL_VERIFICATION_CHECKLIST.md).
