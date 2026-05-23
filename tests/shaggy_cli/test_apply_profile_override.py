"""Regression tests for _apply_profile_override SHAGGY_HOME guard (issue #22502).

When SHAGGY_HOME is set to the shaggy root (e.g. systemd hardcodes
SHAGGY_HOME=/root/.shaggy), _apply_profile_override must still read
active_profile and update SHAGGY_HOME to the profile directory.

When SHAGGY_HOME is already a profile directory (.../profiles/<name>),
_apply_profile_override must trust it and return without re-reading
active_profile (child-process inheritance contract).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


def _run_apply_profile_override(
    tmp_path, monkeypatch, *, shaggy_home: str | None, active_profile: str | None,
    argv: list[str] | None = None,
):
    """Run _apply_profile_override in isolation.

    Returns the value of os.environ["SHAGGY_HOME"] after the call,
    or None if unset.
    """
    shaggy_root = tmp_path / ".shaggy"
    shaggy_root.mkdir(parents=True, exist_ok=True)

    if active_profile is not None:
        (shaggy_root / "active_profile").write_text(active_profile)

    if active_profile and active_profile != "default":
        (shaggy_root / "profiles" / active_profile).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    if shaggy_home is not None:
        monkeypatch.setenv("SHAGGY_HOME", shaggy_home)
    else:
        monkeypatch.delenv("SHAGGY_HOME", raising=False)

    monkeypatch.setattr(sys, "argv", argv or ["shaggy", "gateway", "start"])

    from shaggy_cli.main import _apply_profile_override
    _apply_profile_override()

    return os.environ.get("SHAGGY_HOME")


class TestApplyProfileOverrideShaggyHomeGuard:
    """Regression guard for issue #22502.

    Verifies that SHAGGY_HOME pointing to the shaggy root does NOT suppress
    the active_profile check, while SHAGGY_HOME already pointing to a
    profile directory IS trusted as-is.
    """

    def test_shaggy_home_at_root_with_active_profile_is_redirected(
        self, tmp_path, monkeypatch
    ):
        """SHAGGY_HOME=/root/.shaggy + active_profile=coder must redirect
        SHAGGY_HOME to .../profiles/coder.

        Bug scenario from #22502: systemd sets SHAGGY_HOME to the shaggy root
        and the user switches to a profile via `shaggy profile use`.
        Before the fix, the guard returned early and active_profile was ignored.
        """
        shaggy_root = tmp_path / ".shaggy"
        shaggy_root.mkdir(parents=True, exist_ok=True)

        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            shaggy_home=str(shaggy_root),
            active_profile="coder",
        )

        assert result is not None, "SHAGGY_HOME must be set after profile redirect"
        assert "profiles" in result, (
            f"Expected SHAGGY_HOME to point into profiles/ dir, got: {result!r}"
        )
        assert result.endswith("coder"), (
            f"Expected SHAGGY_HOME to end with 'coder', got: {result!r}"
        )

    def test_shaggy_home_already_profile_dir_is_trusted(self, tmp_path, monkeypatch):
        """SHAGGY_HOME=.../profiles/coder must not be overridden even when
        active_profile says something different.

        Preserves the child-process inheritance contract: a subprocess spawned
        with SHAGGY_HOME already set to a specific profile must stay in that
        profile.
        """
        shaggy_root = tmp_path / ".shaggy"
        profile_dir = shaggy_root / "profiles" / "coder"
        profile_dir.mkdir(parents=True, exist_ok=True)

        (shaggy_root / "active_profile").write_text("other")

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("SHAGGY_HOME", str(profile_dir))
        monkeypatch.setattr(sys, "argv", ["shaggy", "gateway", "start"])

        from shaggy_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("SHAGGY_HOME") == str(profile_dir), (
            "SHAGGY_HOME must remain unchanged when already pointing to a profile dir"
        )

    def test_shaggy_home_unset_reads_active_profile(self, tmp_path, monkeypatch):
        """Classic case: SHAGGY_HOME unset + active_profile=coder must set
        SHAGGY_HOME to the profile directory (existing behaviour must not regress).
        """
        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            shaggy_home=None,
            active_profile="coder",
        )

        assert result is not None
        assert "coder" in result

    def test_shaggy_home_unset_default_profile_no_redirect(self, tmp_path, monkeypatch):
        """active_profile=default must not redirect SHAGGY_HOME."""
        shaggy_root = tmp_path / ".shaggy"
        shaggy_root.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.delenv("SHAGGY_HOME", raising=False)
        monkeypatch.setattr(sys, "argv", ["shaggy", "gateway", "start"])
        (shaggy_root / "active_profile").write_text("default")

        from shaggy_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("SHAGGY_HOME") is None
