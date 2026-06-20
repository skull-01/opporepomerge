# Build Notes — v2.9.1 Build 1

```yaml
addon_version: 2.9.1
baseline: script.oppo203.iso.external-2.9.0-dev-source.zip
package: script.oppo203.iso.external-2.9.1-build1.zip
scope: first-run wizard wording clarity for Kodi startup auto-power
runtime_behavior_changed: wizard_wording_only
hardware_validation: not_performed_not_claimed
planned_success_rate: 93 percent
```

## Summary

Build 1 of v2.9.1 improves the first-run wizard wording for the Kodi startup auto-power feature. The wizard now clearly asks whether Kodi should automatically power on the OPPO/compatible player when Kodi starts and tells the user to choose No if they prefer to keep the player off until playback starts or until they power it on manually.

## Behavior notes

- No OPPO command-map behavior changed.
- No startup power implementation changed.
- No playback routing, XML routing, NAS adapter, service interception, or hardware-control behavior changed.
- The existing `kodi_startup_power_on` setting remains the master toggle.
- Choosing No in the first-run wizard explicitly writes `kodi_startup_power_on=false` and skips Wake-on-LAN/delay/retry follow-up prompts.

## Files changed

- `addon.xml`
- `resources/lib/wizard.py`
- `resources/lib/i18n.py`
- `resources/language/resource.language.*/strings.po`
- `tools/audit_release.py`
- current-version expectations in tests
- `tests/test_v291_build1_startup_autopower_wizard_wording.py`
- README/reference/web-references and v2.9.1 evidence files

## Hardware status

No real OPPO, Chinoppo/M9702/M920x, Kodi, NAS, TV, or ADB hardware validation was performed or claimed.
