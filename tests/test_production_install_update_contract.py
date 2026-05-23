"""Production install/update contract for Shaggy Agent.

These tests protect Rahim's permanent production path:
local source -> official GitHub repo -> website installer -> customer `shaggy update`.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_REPO = "https://github.com/shaggyaratia-69/shaggy-agent"
OFFICIAL_REPO_GIT = f"{OFFICIAL_REPO}.git"
RAW_INSTALL_SH = (
    "https://raw.githubusercontent.com/shaggyaratia-69/shaggy-agent/main/scripts/install.sh"
)
RAW_INSTALL_PS1 = (
    "https://raw.githubusercontent.com/shaggyaratia-69/shaggy-agent/main/scripts/install.ps1"
)
PRODUCTION_CONTRACT = REPO_ROOT / "docs" / "production-install-update-contract.md"

FORBIDDEN_PUBLIC_STRINGS = (
    "Hermes Agent",
    "HERMES-AGENT",
    "Nous Research",
    "NOUS SHAGGY",
    "github.com/NousResearch",
    "shaggy-agent.nousresearch.com",
    "nousresearch.com",
    "Built%20by-Nous",
    "Harvey",
)


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_install_scripts_clone_from_official_github_repo_only() -> None:
    install_sh = read("scripts/install.sh")
    install_ps1 = read("scripts/install.ps1")

    assert f'REPO_URL_HTTPS="{OFFICIAL_REPO_GIT}"' in install_sh
    assert f'$RepoUrlHttps = "{OFFICIAL_REPO_GIT}"' in install_ps1
    assert "github.com/NousResearch" not in install_sh + install_ps1
    assert "nousresearch.com" not in install_sh + install_ps1


def test_update_code_uses_official_github_repo_and_no_old_upstream() -> None:
    main_py = read("shaggy_cli/main.py")
    banner_py = read("shaggy_cli/banner.py")

    assert f'OFFICIAL_REPO_URL = "{OFFICIAL_REPO_GIT}"' in main_py
    assert f'_UPSTREAM_REPO_URL = "{OFFICIAL_REPO_GIT}"' in banner_py
    assert "github.com/NousResearch" not in main_py + banner_py
    assert "nousresearch.com" not in main_py + banner_py


def test_readme_exposes_customer_install_and_update_commands() -> None:
    readme = read("README.md")

    assert RAW_INSTALL_SH in readme
    assert RAW_INSTALL_PS1 in readme
    assert "shaggy update" in readme
    assert OFFICIAL_REPO in readme
    for forbidden in FORBIDDEN_PUBLIC_STRINGS:
        assert forbidden not in readme


def test_production_contract_documents_password_gated_package_without_secret() -> None:
    contract = PRODUCTION_CONTRACT.read_text(encoding="utf-8")

    assert OFFICIAL_REPO in contract
    assert RAW_INSTALL_SH in contract
    assert RAW_INSTALL_PS1 in contract
    assert "shaggy update" in contract
    assert "Shaggy Agent access password" in contract
    assert "X-Shaggy-Access" in contract
    assert "[SHAGGY_ACCESS_PASSWORD]" in contract
    assert "real password must never be committed" in contract.lower()
    for forbidden in FORBIDDEN_PUBLIC_STRINGS:
        assert forbidden not in contract
