"""GitHub Readiness G6 CI hardening checks.

These tests inspect CI/community configuration only. They do not exercise or
change runtime playback, TV, AVR, NAS, or OPPO-control behavior.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _load_yaml(rel: str) -> object:
    return yaml.safe_load(_read(rel))


def test_ci_workflow_is_valid_yaml_and_has_expected_triggers() -> None:
    workflow = _load_yaml(".github/workflows/ci.yml")
    assert isinstance(workflow, dict)
    assert workflow["name"] == "CI"
    assert "push" in workflow[True]
    assert "pull_request" in workflow[True]
    assert "workflow_dispatch" in workflow[True]
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["env"]["EXPECTED_VERSION"] == "2.9.13"
    assert workflow["env"]["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"


def test_ci_workflow_runs_release_gate_commands() -> None:
    text = _read(".github/workflows/ci.yml")
    required_snippets = [
        "python -m py_compile service.py default.py",
        "python tools/render_docs.py --check",
        "python tools/sync_version.py --check --expected-version",
        "python tools/test_layout.py --check",
        "python tools/i18n_extract.py --check",
        "tests/test_github_readiness_g5_tooling_config.py tests/test_github_readiness_g6_ci_hardening.py tests/test_github_readiness_g7_safe_format_cleanup.py tests/test_github_readiness_g8_final_packaging.py",
        "python -m pytest -q tests/test_v2910_final_release.py",
        "python -m pytest -q tests/test_v2910*.py",
        "python -m pytest -q",
        "python -m unittest discover -s tests -p 'test_*.py' -q",
        "python -m coverage run -m pytest -q",
        "python -m coverage report -m",
        "python tools/audit_release.py --expected-version",
        "bash scripts/package_release.sh",
        "Forbidden runtime ZIP members",
        "script.oppo203.iso.external-2.9.13-ci-dev-source.zip",
    ]
    for snippet in required_snippets:
        assert snippet in text


def test_ci_workflow_has_full_gate_and_compatibility_jobs() -> None:
    workflow = _load_yaml(".github/workflows/ci.yml")
    jobs = workflow["jobs"]
    assert set(jobs) == {"test", "lint", "compatibility-smoke"}
    assert jobs["test"]["runs-on"] == "ubuntu-latest"
    assert jobs["test"]["timeout-minutes"] == 30
    assert jobs["lint"]["timeout-minutes"] == 15
    assert jobs["compatibility-smoke"]["timeout-minutes"] == 15
    matrix = jobs["compatibility-smoke"]["strategy"]["matrix"]["python-version"]
    assert matrix == ["3.9", "3.10", "3.12"]


def test_dependabot_config_covers_actions_and_python_dev_dependencies() -> None:
    config = _load_yaml(".github/dependabot.yml")
    assert isinstance(config, dict)
    assert config["version"] == 2
    ecosystems = {(item["package-ecosystem"], item["directory"]) for item in config["updates"]}
    assert ("github-actions", "/") in ecosystems
    assert ("pip", "/") in ecosystems
    for item in config["updates"]:
        assert item["schedule"]["interval"] == "weekly"
        assert item["open-pull-requests-limit"] == 5


def test_verify_script_defaults_to_current_release_version() -> None:
    text = _read("scripts/verify.sh")
    assert 'EXPECTED_VERSION="${EXPECTED_VERSION:-2.9.13}"' in text
    assert 'EXPECTED_VERSION="${EXPECTED_VERSION:-2.9.1}"' not in text


def test_g6_documentation_is_discoverable() -> None:
    assert (ROOT / "docs" / "developer-guide" / "ci.md").exists()
    developer_index = _read("docs/developer-guide/README.md")
    docs_index = _read("docs/README.md")
    readiness = _read("docs/github-readiness/README.md")
    assert "Continuous Integration" in developer_index
    assert "developer-guide/ci.md" in docs_index
    assert "G6 — CI Hardening" in readiness


def test_runtime_packaging_excludes_github_ci_files() -> None:
    from tools import package_installable_zip as package_tool

    assert package_tool.is_runtime_member(".github/workflows/ci.yml") is False
    assert package_tool.is_runtime_member(".github/dependabot.yml") is False
    assert package_tool.is_runtime_member("docs/developer-guide/ci.md") is False
    assert package_tool.is_runtime_member("scripts/verify.sh") is False
