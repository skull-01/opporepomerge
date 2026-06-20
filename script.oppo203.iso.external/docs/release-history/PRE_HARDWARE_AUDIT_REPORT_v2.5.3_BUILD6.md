# Pre-Hardware Audit Report — v2.5.3 Build 6

```yaml
build: v2.5.3 Build 6
baseline: v2.5.3 Build 5
role: pre-hardware release-candidate freeze
hardware_claim: none
software_change_type: packaging/evidence/metadata only
```

## Freeze checklist

| Area | Status | Notes |
|---|---|---|
| Add-on version identity | Frozen at `2.5.3` | Build 3 reconciliation preserved. |
| Service interception | Frozen | Build 1 classifier preserved. |
| Option 4 XML routing | Frozen | Build 2 conservative rules preserved. |
| XML merge/backup/rollback | Frozen | Build 4 hardening preserved. |
| Hardware-readiness export | Frozen | Build 5 helper preserved. |
| Runtime ZIP cleanliness | Required | Runtime ZIP must exclude development evidence. |
| 99 percent coverage gate | Required | Coverage must report `TOTAL 99%`. |
| Real hardware validation | Pending | User-owned physical testing required. |

## Release-candidate decision

Build 6 may be used as the pre-hardware release-candidate package if source verification, post-unpack verification, release audit, and runtime ZIP audit pass. It must not be called hardware-validated until tester results are supplied.
