# Test and Audit Report — v2.2.0 Build 6

## Source verification

```text
python -m pytest -q
504 passed, 12 subtests passed

python -m unittest discover -s tests
Ran 504 tests ... OK

python -m coverage run -m pytest -q
504 passed, 12 subtests passed

python -m coverage report -m
TOTAL 99%
Raw combined line+branch coverage: 98.74398717263495%

python tools/audit_release.py --expected-version 2.2.0.6
SUMMARY: PASS (85/85 checks passed)
```

## Release audit output

```text
OK: python_compile - compileall passed
OK: xml:addon.xml - parsed
OK: xml:resources/settings.xml - parsed
OK: locale:resource.language.de_de - 154 msgctxt ids
OK: locale:resource.language.en_gb - 154 msgctxt ids
OK: locale:resource.language.es_es - 154 msgctxt ids
OK: locale:resource.language.fr_fr - 154 msgctxt ids
OK: locale:resource.language.it_it - 154 msgctxt ids
OK: locale:resource.language.ja_jp - 154 msgctxt ids
OK: locale:resource.language.ko_kr - 154 msgctxt ids
OK: locale:resource.language.nl_nl - 154 msgctxt ids
OK: locale:resource.language.pl_pl - 154 msgctxt ids
OK: locale:resource.language.pt_br - 154 msgctxt ids
OK: locale:resource.language.ru_ru - 154 msgctxt ids
OK: locale:resource.language.zh_cn - 154 msgctxt ids
OK: settings_string_ids - 109 label/help ids covered
OK: command_map - 76 canonical keys; no forbidden tokens
OK: hardware_model_count - settings enum and HARDWARE_COMPAT both have 12 entries
OK: coverage_gate - fail_under=99
OK: file:.coveragerc - present
OK: file:README.md - present
OK: file:reference.md - present
OK: file:web-references.md - present
OK: file:HARDWARE_VALIDATION_v2.0.0_BUILD4.md - present
OK: file:MVP_COMPLIANCE_MATRIX_v2.0.0_BUILD4.md - present
OK: file:RELEASE_NOTES_v2.0.0.md - present
OK: file:RELEASE_MANIFEST_v2.0.0.md - present
OK: file:MVP_COMPLIANCE_MATRIX_v2.0.0.md - present
OK: file:HARDWARE_VALIDATION_v2.0.0.md - present
OK: file:BUILD_NOTES_v2.0.0_BUILD6.md - present
OK: file:RELEASE_MANIFEST_v2.0.0_BUILD6.md - present
OK: file:BUILD_NOTES_v2.1.0_BUILD1.md - present
OK: file:RELEASE_MANIFEST_v2.1.0_BUILD1.md - present
OK: file:COVERAGE_REPORT_v2.1.0_BUILD1.md - present
OK: file:TEST_AUDIT_REPORT_v2.1.0_BUILD1.md - present
OK: file:BUILD_NOTES_v2.1.0_BUILD2.md - present
OK: file:RELEASE_MANIFEST_v2.1.0_BUILD2.md - present
OK: file:COVERAGE_REPORT_v2.1.0_BUILD2.md - present
OK: file:TEST_AUDIT_REPORT_v2.1.0_BUILD2.md - present
OK: file:BUILD_NOTES_v2.1.0_BUILD3.md - present
OK: file:RELEASE_MANIFEST_v2.1.0_BUILD3.md - present
OK: file:COVERAGE_REPORT_v2.1.0_BUILD3.md - present
OK: file:TEST_AUDIT_REPORT_v2.1.0_BUILD3.md - present
OK: file:BUILD_NOTES_v2.1.0_BUILD5.md - present
OK: file:RELEASE_MANIFEST_v2.1.0_BUILD5.md - present
OK: file:COVERAGE_REPORT_v2.1.0_BUILD5.md - present
OK: file:TEST_AUDIT_REPORT_v2.1.0_BUILD5.md - present
OK: file:BUILD_NOTES_v2.1.0_BUILD6.md - present
OK: file:RELEASE_MANIFEST_v2.1.0_BUILD6.md - present
OK: file:COVERAGE_REPORT_v2.1.0_BUILD6.md - present
OK: file:TEST_AUDIT_REPORT_v2.1.0_BUILD6.md - present
OK: file:BUILD_NOTES_v2.1.0_BUILD7.md - present
OK: file:RELEASE_MANIFEST_v2.1.0_BUILD7.md - present
OK: file:COVERAGE_REPORT_v2.1.0_BUILD7.md - present
OK: file:TEST_AUDIT_REPORT_v2.1.0_BUILD7.md - present
OK: file:BUILD_NOTES_v2.1.0_BUILD8.md - present
OK: file:RELEASE_MANIFEST_v2.1.0_BUILD8.md - present
OK: file:COVERAGE_REPORT_v2.1.0_BUILD8.md - present
OK: file:TEST_AUDIT_REPORT_v2.1.0_BUILD8.md - present
OK: file:BUILD_NOTES_v2.2.0_BUILD1.md - present
OK: file:RELEASE_MANIFEST_v2.2.0_BUILD1.md - present
OK: file:COVERAGE_REPORT_v2.2.0_BUILD1.md - present
OK: file:TEST_AUDIT_REPORT_v2.2.0_BUILD1.md - present
OK: file:BUILD_NOTES_v2.2.0_BUILD2.md - present
OK: file:RELEASE_MANIFEST_v2.2.0_BUILD2.md - present
OK: file:COVERAGE_REPORT_v2.2.0_BUILD2.md - present
OK: file:TEST_AUDIT_REPORT_v2.2.0_BUILD2.md - present
OK: file:BUILD_NOTES_v2.2.0_BUILD3.md - present
OK: file:RELEASE_MANIFEST_v2.2.0_BUILD3.md - present
OK: file:COVERAGE_REPORT_v2.2.0_BUILD3.md - present
OK: file:TEST_AUDIT_REPORT_v2.2.0_BUILD3.md - present
OK: file:BUILD_NOTES_v2.2.0_BUILD4.md - present
OK: file:RELEASE_MANIFEST_v2.2.0_BUILD4.md - present
OK: file:COVERAGE_REPORT_v2.2.0_BUILD4.md - present
OK: file:TEST_AUDIT_REPORT_v2.2.0_BUILD4.md - present
OK: file:BUILD_NOTES_v2.2.0_BUILD5.md - present
OK: file:RELEASE_MANIFEST_v2.2.0_BUILD5.md - present
OK: file:COVERAGE_REPORT_v2.2.0_BUILD5.md - present
OK: file:TEST_AUDIT_REPORT_v2.2.0_BUILD5.md - present
OK: file:BUILD_NOTES_v2.2.0_BUILD6.md - present
OK: file:RELEASE_MANIFEST_v2.2.0_BUILD6.md - present
OK: file:COVERAGE_REPORT_v2.2.0_BUILD6.md - present
OK: file:TEST_AUDIT_REPORT_v2.2.0_BUILD6.md - present
OK: addon_xml_declaration - version=1.0
OK: addon_version - 2.2.0.6
SUMMARY: PASS (85/85 checks passed)

```

## Hardware test status

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
