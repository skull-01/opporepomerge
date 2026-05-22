"""v2.9.1 Build 1 - first-run Kodi startup auto-power wording clarity."""
from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
import zipfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
from tests._support.project_files import find_project_file, read_project_file
LIB = ROOT / "resources" / "lib"
for path in (str(ROOT), str(LIB)):
    if path not in sys.path:
        sys.path.insert(0, path)


class FakeAddon:
    def __init__(self, initial=None):
        self.values = dict(initial or {})

    def getSetting(self, key):
        return self.values.get(key, "")

    def setSetting(self, key, value):
        self.values[key] = str(value)


def _fresh_wizard():
    sys.modules.pop("wizard", None)
    return importlib.import_module("wizard")


def _read(name: str) -> str:
    return read_project_file(ROOT, name)


def test_startup_autopower_copy_is_explicitly_optional():
    wizard = _fresh_wizard()
    assert wizard.WIZARD_TEXT["autopower_title"] == "Kodi startup auto-power"
    body = wizard.WIZARD_TEXT["autopower_body"]
    assert "automatically power on the OPPO/compatible player when Kodi starts" in body
    assert "Choose No" in body
    assert "keep the player off until playback starts or you power it on manually" in body


def test_full_first_run_no_choice_disables_autopower_and_skips_wol_followup():
    wizard = _fresh_wizard()
    addon = FakeAddon({
        "oppo_ip": "192.0.2.10",
        "oppo_port": "23",
        # Prove the wizard can explicitly turn a previously enabled value off.
        "kodi_startup_power_on": "true",
    })
    prompts = []
    responses = iter([
        True,   # prerequisites
        False,  # stock jailbreak disabled
        False,  # AutoScript shell handler disabled
        True,   # Quick Start confirmed
        False,  # Kodi startup auto-power disabled
        False,  # skip architecture auto-test
        True,   # use External Player
    ])
    inputs = iter(["192.0.2.10", "23"])

    def yn(title, message):
        prompts.append((title, message))
        return next(responses)

    with mock.patch.object(wizard, "_addon", return_value=addon), \
         mock.patch.object(wizard, "_choose_mode", return_value="full"), \
         mock.patch.object(wizard, "_probe", return_value=True), \
         mock.patch.object(wizard, "_sel", return_value=0), \
         mock.patch.object(wizard, "_yn", side_effect=yn), \
         mock.patch.object(wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
         mock.patch.object(wizard, "_ok", side_effect=lambda *a, **k: None):
        assert wizard.run_wizard() is True

    assert addon.values["kodi_startup_power_on"] == "false"
    assert addon.values.get("kodi_startup_power_on_use_wol") is None
    assert addon.values.get("kodi_startup_power_on_delay") is None
    assert addon.values.get("kodi_startup_power_on_retries") is None
    titles = [title for title, _ in prompts]
    assert "Kodi startup auto-power" in titles
    assert "Wake-on-LAN before power-on" not in titles


def test_full_first_run_yes_choice_preserves_existing_advanced_followups():
    wizard = _fresh_wizard()
    addon = FakeAddon({"oppo_ip": "192.0.2.11", "oppo_port": "23"})
    prompts = []
    responses = iter([
        True,   # prerequisites
        False,  # stock jailbreak disabled
        False,  # AutoScript shell handler disabled
        True,   # Quick Start confirmed
        True,   # Kodi startup auto-power enabled
        True,   # Wake-on-LAN first
        False,  # skip architecture auto-test
        True,   # use External Player
    ])
    inputs = iter(["192.0.2.11", "23", "6", "3", ""])

    def yn(title, message):
        prompts.append((title, message))
        return next(responses)

    with mock.patch.object(wizard, "_addon", return_value=addon), \
         mock.patch.object(wizard, "_choose_mode", return_value="full"), \
         mock.patch.object(wizard, "_probe", return_value=True), \
         mock.patch.object(wizard, "_sel", return_value=0), \
         mock.patch.object(wizard, "_yn", side_effect=yn), \
         mock.patch.object(wizard, "_in", side_effect=lambda *a, **k: next(inputs)), \
         mock.patch.object(wizard, "_ok", side_effect=lambda *a, **k: None):
        assert wizard.run_wizard() is True

    assert addon.values["kodi_startup_power_on"] == "true"
    assert addon.values["kodi_startup_power_on_delay"] == "6"
    assert addon.values["kodi_startup_power_on_retries"] == "3"
    assert addon.values["kodi_startup_power_on_use_wol"] == "true"
    titles = [title for title, _ in prompts]
    assert "Wake-on-LAN before power-on" in titles


def test_service_startup_guard_still_does_nothing_when_disabled():
    service_spec = importlib.util.spec_from_file_location("service_under_test", ROOT / "service.py")
    service = importlib.util.module_from_spec(service_spec)
    assert service_spec.loader is not None
    service_spec.loader.exec_module(service)

    class Settings:
        def get_bool(self, key, default=False):
            assert key == "kodi_startup_power_on"
            return False

    with mock.patch.object(service, "log") as log:
        service._kodi_startup_power_on(Settings())
    log.assert_not_called()


def test_v291_evidence_and_runtime_package_policy(tmp_path):
    for name in (
        "BUILD_NOTES_v2.9.1_BUILD1.md",
        "RELEASE_MANIFEST_v2.9.1_BUILD1.md",
        "RELEASE_NOTES_v2.9.1_BUILD1.md",
        "COVERAGE_REPORT_v2.9.1_BUILD1.md",
        "TEST_AUDIT_REPORT_v2.9.1_BUILD1.md",
        "HARDWARE_VALIDATION_v2.9.1_BUILD1.md",
        "PRE_HARDWARE_AUDIT_REPORT_v2.9.1_BUILD1.md",
    ):
        assert find_project_file(ROOT, name).exists(), name
    assert 'version="2.9.12"' in _read("addon.xml")
    assert "Kodi startup auto-power" in _read("addon.xml")
    assert "runtime_behavior_changed: wizard_wording_only" in _read("BUILD_NOTES_v2.9.1_BUILD1.md")

    spec = importlib.util.spec_from_file_location("package_installable_zip", ROOT / "tools" / "package_installable_zip.py")
    tool = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(tool)
    out = tmp_path / "runtime.zip"
    names = tool.create_installable_zip(ROOT, out)
    for suffix in (
        "BUILD_NOTES_v2.9.1_BUILD1.md",
        "TEST_AUDIT_REPORT_v2.9.1_BUILD1.md",
        "tests/test_v291_build1_startup_autopower_wizard_wording.py",
        "tools/audit_release.py",
    ):
        assert f"script.oppo203.iso.external/{suffix}" not in names
    with zipfile.ZipFile(out) as zf:
        addon_text = zf.read("script.oppo203.iso.external/addon.xml").decode("utf-8")
    assert 'version="2.9.12"' in addon_text


def test_v291_release_audit_requires_build1_evidence():
    spec = importlib.util.spec_from_file_location("audit_release", ROOT / "tools" / "audit_release.py")
    audit = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(audit)
    results = audit.run_audit(audit.project_root(audit.Path(ROOT)), expected_version="2.9.12")
    failed = [item for item in results if item["status"] != "ok"]
    assert failed == []
    names = {item["name"] for item in results}
    for required in (
        "file:BUILD_NOTES_v2.9.1_BUILD1.md",
        "file:RELEASE_MANIFEST_v2.9.1_BUILD1.md",
        "file:TEST_AUDIT_REPORT_v2.9.1_BUILD1.md",
        "file:HARDWARE_VALIDATION_v2.9.1_BUILD1.md",
        "file:PRE_HARDWARE_AUDIT_REPORT_v2.9.1_BUILD1.md",
    ):
        assert required in names
