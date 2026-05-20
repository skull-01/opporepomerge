# Test and Audit Report — v2.2.0 Build 4

## Source verification

```text
python -m pytest -q
486 passed, 12 subtests passed

python -m unittest discover -s tests
Ran 486 tests ... OK

python -m coverage run -m pytest -q
486 passed, 12 subtests passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.2.0.4
SUMMARY: PASS (77/77 checks passed)
```

## Source coverage details

```text
Name                                       Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------------
resources/lib/adb_control.py                  26      0      8      0   100%
resources/lib/arch_benchmark.py               67      0     26      0   100%
resources/lib/autoscript_helper.py            98      0     28      0   100%
resources/lib/diagnostics.py                  69      0     20      0   100%
resources/lib/discovery.py                   143      0     62      0   100%
resources/lib/external_player.py             214      0     72      1    99%   157->163
resources/lib/first_run_wizard.py            117      0     44      2    99%   124->131, 170->169
resources/lib/hardware_presets.py             29      0      8      0   100%
resources/lib/i18n.py                         21      0      4      0   100%
resources/lib/installer.py                   209      0     64      0   100%
resources/lib/intercept.py                    73      0     44      0   100%
resources/lib/keymap_skin.py                  34      0      8      0   100%
resources/lib/logging_v116.py                 99      0     38      0   100%
resources/lib/oppo_control.py                539      3    214      7    99%   422, 462->461, 480, 489->481, 490, 567->570, 864->868
resources/lib/oppo_remote.py                 142      0     34      1    99%   37->exit
resources/lib/oppo_tcp_client.py             144      1     50      1    99%   124
resources/lib/playercorefactory_merge.py      91      0     32      0   100%
resources/lib/preset_manager.py              107      2     48      0    99%   190-191
resources/lib/reconnect_backoff.py            24      0     10      0   100%
resources/lib/settings_reader.py             136      7     58      4    94%   111, 178, 184-185, 191-192, 197->195, 210
resources/lib/tv_control.py                   55      0     18      0   100%
resources/lib/wizard.py                      166      0     48      1    99%   195->197
resources/lib/wizard_polish.py                67      0     18      0   100%
--------------------------------------------------------------------------------------
TOTAL                                       2670     13    956     17    99%

```

## Source audit details

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
OK: addon_xml_declaration - version=1.0
OK: addon_version - 2.2.0.4
SUMMARY: PASS (77/77 checks passed)

```

## Post-unpack verification

```text
python -m pytest -q
486 passed, 12 subtests passed

python -m unittest discover -s tests
Ran 486 tests ... OK

python -m coverage run -m pytest -q
486 passed, 12 subtests passed

python -m coverage report -m
TOTAL 99%

python tools/audit_release.py --expected-version 2.2.0.4
SUMMARY: PASS (77/77 checks passed)
```

## Hardware status

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
