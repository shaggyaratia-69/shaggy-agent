"""Resolve SHAGGY_HOME for standalone skill scripts.

Skill scripts may run outside the Shaggy process (e.g. system Python,
nix env, CI) where ``shaggy_constants`` is not importable.  This module
provides the same ``get_shaggy_home()`` and ``display_shaggy_home()``
contracts as ``shaggy_constants`` without requiring it on ``sys.path``.

When ``shaggy_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``shaggy_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``SHAGGY_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from shaggy_constants import display_shaggy_home as display_shaggy_home
    from shaggy_constants import get_shaggy_home as get_shaggy_home
except (ModuleNotFoundError, ImportError):

    def get_shaggy_home() -> Path:
        """Return the Shaggy home directory (default: ~/.shaggy).

        Mirrors ``shaggy_constants.get_shaggy_home()``."""
        val = os.environ.get("SHAGGY_HOME", "").strip()
        return Path(val) if val else Path.home() / ".shaggy"

    def display_shaggy_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``shaggy_constants.display_shaggy_home()``."""
        home = get_shaggy_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
