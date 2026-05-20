# Test and Audit Report - v2.1.0 Build 3

## Source verification

```text
python -m pytest -q
400 passed

python -m unittest discover -s tests
Ran 400 tests ... OK

python -m coverage run -m pytest -q
400 passed

python -m coverage report -m
TOTAL 96%

python tools/audit_release.py --expected-version 2.1.0.3
SUMMARY: PASS (44/44 checks passed)
```

## Source coverage report

```text
Name                                       Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------------
resources/lib/adb_control.py                  26      0      8      1    97%   50->53
resources/lib/arch_benchmark.py               67      1     26      1    98%   47
resources/lib/autoscript_helper.py            98      0     28      2    98%   58->61, 104->108
resources/lib/diagnostics.py                  69      0     20      0   100%
resources/lib/discovery.py                   143      8     62      3    95%   82, 90->88, 156, 197, 199, 201-204
resources/lib/external_player.py             214      9     72     11    93%   37, 44->exit, 75->78, 121->123, 154->166, 157->163, 178, 225->233, 256, 267, 270-271, 303-304, 326
resources/lib/hardware_presets.py             29      0      8      0   100%
resources/lib/i18n.py                         21      0      4      0   100%
resources/lib/installer.py                   209     11     64     11    92%   91->111, 212-224, 353, 385->387, 394, 427-429, 467, 506-508, 536->542, 540
resources/lib/intercept.py                    73      0     44      4    97%   42->exit, 43->exit, 47->exit, 142->141
resources/lib/keymap_skin.py                  34      0      8      0   100%
resources/lib/logging_v116.py                 99      4     38      3    95%   77, 84-85, 152, 179->exit
resources/lib/oppo_control.py                539     22    214     20    94%   110, 159, 186-187, 205-208, 215-216, 422, 427, 462->461, 466, 480, 489->481, 490, 539-541, 567->570, 575, 592->594, 619, 713->717, 717->725, 728, 823->814, 864->868, 898
resources/lib/oppo_remote.py                 142      0     34      1    99%   99->103
resources/lib/oppo_tcp_client.py             144      5     50      3    96%   124, 127-128, 186, 248
resources/lib/playercorefactory_merge.py      91      1     32      3    97%   166, 177->182, 183->188
resources/lib/preset_manager.py              107      5     48      3    95%   44->exit, 46, 62, 92, 190-191
resources/lib/reconnect_backoff.py            24      0     10      0   100%
resources/lib/settings_reader.py             101      3     42      3    96%   109, 125, 128, 140->139, 154->152
resources/lib/tv_control.py                   55      0     18      0   100%
resources/lib/wizard.py                      166      4     48      4    96%   12->exit, 16->19, 75-76, 81-82, 185->189, 195->197
resources/lib/wizard_polish.py                67      0     18      0   100%
--------------------------------------------------------------------------------------
TOTAL                                       2518     73    896     73    96%

```

## Source audit output

```text
OK: python_compile - compileall passed
OK: xml:addon.xml - parsed
OK: xml:resources/settings.xml - parsed
OK: locale:resource.language.de_de - 150 msgctxt ids
OK: locale:resource.language.en_gb - 150 msgctxt ids
OK: locale:resource.language.es_es - 150 msgctxt ids
OK: locale:resource.language.fr_fr - 150 msgctxt ids
OK: locale:resource.language.it_it - 150 msgctxt ids
OK: locale:resource.language.ja_jp - 150 msgctxt ids
OK: locale:resource.language.ko_kr - 150 msgctxt ids
OK: locale:resource.language.nl_nl - 150 msgctxt ids
OK: locale:resource.language.pl_pl - 150 msgctxt ids
OK: locale:resource.language.pt_br - 150 msgctxt ids
OK: locale:resource.language.ru_ru - 150 msgctxt ids
OK: locale:resource.language.zh_cn - 150 msgctxt ids
OK: settings_string_ids - 105 label/help ids covered
OK: command_map - 76 canonical keys; no forbidden tokens
OK: hardware_model_count - settings enum and HARDWARE_COMPAT both have 12 entries
OK: coverage_gate - fail_under=96
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
OK: addon_version - 2.1.0.3
SUMMARY: PASS (44/44 checks passed)

```

## Post-unpack verification

```text
python -m pytest -q
400 passed

python -m unittest discover -s tests
Ran 400 tests ... OK

python -m coverage run -m pytest -q
400 passed

python -m coverage report -m
TOTAL 96%

python tools/audit_release.py --expected-version 2.1.0.3
SUMMARY: PASS (44/44 checks passed)
```

## Post-unpack coverage report

```text
Name                                       Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------------
resources/lib/adb_control.py                  26      0      8      1    97%   50->53
resources/lib/arch_benchmark.py               67      1     26      1    98%   47
resources/lib/autoscript_helper.py            98      0     28      2    98%   58->61, 104->108
resources/lib/diagnostics.py                  69      0     20      0   100%
resources/lib/discovery.py                   143      8     62      3    95%   82, 90->88, 156, 197, 199, 201-204
resources/lib/external_player.py             214      9     72     11    93%   37, 44->exit, 75->78, 121->123, 154->166, 157->163, 178, 225->233, 256, 267, 270-271, 303-304, 326
resources/lib/hardware_presets.py             29      0      8      0   100%
resources/lib/i18n.py                         21      0      4      0   100%
resources/lib/installer.py                   209     11     64     11    92%   91->111, 212-224, 353, 385->387, 394, 427-429, 467, 506-508, 536->542, 540
resources/lib/intercept.py                    73      0     44      4    97%   42->exit, 43->exit, 47->exit, 142->141
resources/lib/keymap_skin.py                  34      0      8      0   100%
resources/lib/logging_v116.py                 99      4     38      3    95%   77, 84-85, 152, 179->exit
resources/lib/oppo_control.py                539     22    214     20    94%   110, 159, 186-187, 205-208, 215-216, 422, 427, 462->461, 466, 480, 489->481, 490, 539-541, 567->570, 575, 592->594, 619, 713->717, 717->725, 728, 823->814, 864->868, 898
resources/lib/oppo_remote.py                 142      0     34      1    99%   99->103
resources/lib/oppo_tcp_client.py             144      5     50      3    96%   124, 127-128, 186, 248
resources/lib/playercorefactory_merge.py      91      1     32      3    97%   166, 177->182, 183->188
resources/lib/preset_manager.py              107      5     48      3    95%   44->exit, 46, 62, 92, 190-191
resources/lib/reconnect_backoff.py            24      0     10      0   100%
resources/lib/settings_reader.py             101      3     42      3    96%   109, 125, 128, 140->139, 154->152
resources/lib/tv_control.py                   55      0     18      0   100%
resources/lib/wizard.py                      166      4     48      4    96%   12->exit, 16->19, 75-76, 81-82, 185->189, 195->197
resources/lib/wizard_polish.py                67      0     18      0   100%
--------------------------------------------------------------------------------------
TOTAL                                       2518     73    896     73    96%

```

## Post-unpack audit output

```text
OK: python_compile - compileall passed
OK: xml:addon.xml - parsed
OK: xml:resources/settings.xml - parsed
OK: locale:resource.language.de_de - 150 msgctxt ids
OK: locale:resource.language.en_gb - 150 msgctxt ids
OK: locale:resource.language.es_es - 150 msgctxt ids
OK: locale:resource.language.fr_fr - 150 msgctxt ids
OK: locale:resource.language.it_it - 150 msgctxt ids
OK: locale:resource.language.ja_jp - 150 msgctxt ids
OK: locale:resource.language.ko_kr - 150 msgctxt ids
OK: locale:resource.language.nl_nl - 150 msgctxt ids
OK: locale:resource.language.pl_pl - 150 msgctxt ids
OK: locale:resource.language.pt_br - 150 msgctxt ids
OK: locale:resource.language.ru_ru - 150 msgctxt ids
OK: locale:resource.language.zh_cn - 150 msgctxt ids
OK: settings_string_ids - 105 label/help ids covered
OK: command_map - 76 canonical keys; no forbidden tokens
OK: hardware_model_count - settings enum and HARDWARE_COMPAT both have 12 entries
OK: coverage_gate - fail_under=96
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
OK: addon_version - 2.1.0.3
SUMMARY: PASS (44/44 checks passed)

```

## Scope notes

No real OPPO, Chinoppo/M9702, TCL/Android TV, Kodi installation, or real ADB hardware was tested.
