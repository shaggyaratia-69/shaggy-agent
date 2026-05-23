"""Contract checks for the Shaggy-from-Hermes update pipeline.

These tests protect the repeatable release flow Rahim wants: upstream Hermes
improvements can be copied into Shaggy, but the customer-facing package must
remain Shaggy-branded and the dashboard Kanban must stay writable.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PUBLIC_TERMS = (
    "Hermes" + " Agent",
    "Nous" + " Research",
    "NOUS" + " SHAGGY",
    "Har" + "vey",
)


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_shaggy_cli_aliases_include_hyphen_and_underscore_forms() -> None:
    data = tomllib.loads(_read("pyproject.toml"))
    scripts = data["project"]["scripts"]

    expected = {
        "shaggy": "shaggy_cli.main:main",
        "shaggy-agent": "shaggy_cli.main:main",
        "shaggy_agent": "shaggy_cli.main:main",
        "shaggy-core": "run_agent:main",
        "shaggy_core": "run_agent:main",
        "shaggy-acp": "acp_adapter.entry:main",
        "shaggy_acp": "acp_adapter.entry:main",
    }
    for command, target in expected.items():
        assert scripts.get(command) == target


def test_dashboard_kanban_plugin_is_shaggy_branded_and_writable() -> None:
    manifest = json.loads(_read("plugins/kanban/dashboard/manifest.json"))
    assert manifest["name"] == "kanban"
    assert manifest["label"] == "Kanban"
    assert manifest["tab"]["path"] == "/kanban"

    api = _read("plugins/kanban/dashboard/plugin_api.py")
    # Writable board requirements: add, move/update, delete/archive/complete.
    for route in (
        '@router.post("/tasks")',
        '@router.patch("/tasks/{task_id}")',
        '@router.delete("/tasks/{task_id}")',
    ):
        assert route in api
    for behavior in ("complete_task", "archive_task", "_set_status_direct"):
        assert behavior in api
    assert "from shaggy_cli import kanban_db" in api
    assert "window.__SHAGGY_SESSION_TOKEN__" in api

    bundle_text = "\n".join(
        _read(path)
        for path in (
            "plugins/kanban/dashboard/dist/index.js",
            "plugins/kanban/dashboard/dist/style.css",
        )
    )
    assert "Shaggy" in bundle_text
    for term in FORBIDDEN_PUBLIC_TERMS:
        assert term not in bundle_text


def test_dashboard_shell_has_plugin_route_without_public_old_branding() -> None:
    app = _read("web/src/App.tsx")
    html = _read("web/index.html")
    manifest = _read("plugins/kanban/dashboard/manifest.json")

    assert "usePlugins" in app
    assert "buildRoutes" in app
    assert '"/kanban"' in manifest
    assert "Shaggy" in html or "Shaggy" in app

    public_text = "\n".join([app, html, manifest])
    for term in FORBIDDEN_PUBLIC_TERMS:
        assert term not in public_text


def test_dashboard_default_theme_matches_cherries_public_site_without_route_changes() -> None:
    presets = _read("web/src/themes/presets.ts")
    server = _read("shaggy_cli/web_server.py")
    backdrop = _read("web/src/components/Backdrop.tsx")

    assert 'label: "Cherries Cyanotype"' in presets
    assert 'background: { hex: "#F7F2DF", alpha: 1 }' in presets
    assert 'midground: { hex: "#063F73", alpha: 1 }' in presets
    assert 'foreground: { hex: "#1264A3", alpha: 0.14 }' in presets
    assert 'baseBlendMode: "normal"' in presets
    assert 'Cherries Cyanotype' in server
    assert "--component-backdrop-base-blend-mode" in backdrop

    app = _read("web/src/App.tsx")
    assert '"/sessions"' in app
    assert '"/kanban"' in _read("plugins/kanban/dashboard/manifest.json")


def test_update_pipeline_plan_exists_and_blocks_live_deploy_by_default() -> None:
    plan = _read("docs/plans/2026-05-22-shaggy-hermes-update-pipeline.md")
    assert "Shaggy Agent Update Pipeline" in plan
    assert "Do not deploy" in plan
    assert "Cloudflare" in plan
    assert "Kanban" in plan
    assert "SHA256" in plan
