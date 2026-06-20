# Coverage Report — v2.2.0 Build 7

The 99% coverage gate remains enforced. Build 7 adds service watcher persistence edge-case tests and hardens blank add-on-data persistence behavior.

```text
TOTAL 99%
Raw combined line+branch coverage: 98.79743452699091%
```

## Coverage output

```text
Name                                       Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------------
resources/lib/adb_control.py                  26      0      8      0   100%
resources/lib/arch_benchmark.py               67      0     26      0   100%
resources/lib/autoscript_helper.py            98      0     28      0   100%
resources/lib/diagnostics.py                  69      0     20      0   100%
resources/lib/discovery.py                   143      0     62      0   100%
resources/lib/external_player.py             214      0     72      1    99%   157->163
resources/lib/first_run_wizard.py            169      3     66      3    97%   124->131, 170->169, 195, 208-209
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
resources/lib/settings_reader.py             136      6     58      3    95%   111, 188-189, 195-196, 201->199, 214
resources/lib/tv_control.py                   55      0     18      0   100%
resources/lib/wizard.py                      204     10     52      2    95%   51, 54-57, 60, 69, 72, 77->exit, 79-80, 260->262
resources/lib/wizard_polish.py                67      0     18      0   100%
--------------------------------------------------------------------------------------
TOTAL                                       2760     25    982     18    99%

```
