"""Shared file safety rules used by both tools and ACP shims."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def _shaggy_home_path() -> Path:
    """Resolve the active SHAGGY_HOME (profile-aware) without circular imports."""
    try:
        from shaggy_constants import get_shaggy_home  # local import to avoid cycles
        return get_shaggy_home()
    except Exception:
        return Path(os.path.expanduser("~/.shaggy"))


def build_write_denied_paths(home: str) -> set[str]:
    """Return exact sensitive paths that must never be written."""
    shaggy_home = _shaggy_home_path()
    return {
        os.path.realpath(p)
        for p in [
            os.path.join(home, ".ssh", "authorized_keys"),
            os.path.join(home, ".ssh", "id_rsa"),
            os.path.join(home, ".ssh", "id_ed25519"),
            os.path.join(home, ".ssh", "config"),
            str(shaggy_home / ".env"),
            os.path.join(home, ".bashrc"),
            os.path.join(home, ".zshrc"),
            os.path.join(home, ".profile"),
            os.path.join(home, ".bash_profile"),
            os.path.join(home, ".zprofile"),
            os.path.join(home, ".netrc"),
            os.path.join(home, ".pgpass"),
            os.path.join(home, ".npmrc"),
            os.path.join(home, ".pypirc"),
            "/etc/sudoers",
            "/etc/passwd",
            "/etc/shadow",
        ]
    }


def build_write_denied_prefixes(home: str) -> list[str]:
    """Return sensitive directory prefixes that must never be written."""
    return [
        os.path.realpath(p) + os.sep
        for p in [
            os.path.join(home, ".ssh"),
            os.path.join(home, ".aws"),
            os.path.join(home, ".gnupg"),
            os.path.join(home, ".kube"),
            "/etc/sudoers.d",
            "/etc/systemd",
            os.path.join(home, ".docker"),
            os.path.join(home, ".azure"),
            os.path.join(home, ".config", "gh"),
        ]
    ]


def get_safe_write_root() -> Optional[str]:
    """Return the resolved SHAGGY_WRITE_SAFE_ROOT path, or None if unset."""
    root = os.getenv("SHAGGY_WRITE_SAFE_ROOT", "")
    if not root:
        return None
    try:
        return os.path.realpath(os.path.expanduser(root))
    except Exception:
        return None


def is_write_denied(path: str) -> bool:
    """Return True if path is blocked by the write denylist or safe root."""
    home = os.path.realpath(os.path.expanduser("~"))
    resolved = os.path.realpath(os.path.expanduser(str(path)))

    if resolved in build_write_denied_paths(home):
        return True
    for prefix in build_write_denied_prefixes(home):
        if resolved.startswith(prefix):
            return True

    safe_root = get_safe_write_root()
    if safe_root and not (resolved == safe_root or resolved.startswith(safe_root + os.sep)):
        return True

    return False


def get_read_block_error(path: str) -> Optional[str]:
    """Return an error message when a read targets internal Shaggy files."""
    resolved = Path(path).expanduser().resolve()
    shaggy_home = _shaggy_home_path().resolve()
    blocked_dirs = [
        shaggy_home / "skills" / ".hub" / "index-cache",
        shaggy_home / "skills" / ".hub",
    ]
    for blocked in blocked_dirs:
        try:
            resolved.relative_to(blocked)
        except ValueError:
            continue
        return (
            f"Access denied: {path} is an internal Shaggy cache file "
            "and cannot be read directly to prevent prompt injection. "
            "Use the skills_list or skill_view tools instead."
        )

    if os.getenv("SHAGGY_ALLOW_INTERNAL_SOURCE", "").strip().lower() not in {"1", "true", "yes", "on"}:
        parts = {part.lower() for part in resolved.parts}
        resolved_text = str(resolved).lower()
        internal_markers = (
            "/site-packages/agent/",
            "/site-packages/tools/",
            "/site-packages/shaggy_cli/",
            "/site-packages/acp_adapter/",
            "/site-packages/gateway/",
            "/site-packages/tui_gateway/",
        )
        internal_files = {
            "cli.py",
            "run_agent.py",
            "model_tools.py",
            "shaggy_constants.py",
            "toolsets.py",
        }
        if any(marker in resolved_text for marker in internal_markers) or ("site-packages" in parts and resolved.name in internal_files):
            return (
                "Access denied: Shaggy Agent internal product files are protected. "
                "I can help you use Shaggy Agent, run setup, troubleshoot normal errors, "
                "or check status, but I cannot reveal or copy internal source code or package files."
            )
    return None
