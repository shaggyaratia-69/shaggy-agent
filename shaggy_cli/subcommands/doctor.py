"""``shaggy doctor`` subcommand parser.

Extracted verbatim from ``shaggy_cli/main.py:main()`` (god-file Phase 2).
Handler injected to avoid importing ``main``.
"""

from __future__ import annotations

from typing import Callable


def build_doctor_parser(subparsers, *, cmd_doctor: Callable) -> None:
    """Attach the ``doctor`` subcommand to ``subparsers``."""
    # =========================================================================
    # doctor command
    # =========================================================================
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Diagnose and repair Shaggy Agent setup",
        description="Diagnose and repair issues with Shaggy Agent setup",
    )
    doctor_parser.add_argument(
        "--fix",
        action="store_true",
        default=True,
        help="Attempt safe automatic repairs (default)",
    )
    doctor_parser.add_argument(
        "--no-fix",
        "--check",
        dest="no_fix",
        action="store_true",
        help="Diagnose only; do not apply repairs",
    )
    doctor_parser.add_argument(
        "--ack",
        metavar="ADVISORY_ID",
        default=None,
        help=(
            "Acknowledge a security advisory by ID and exit. After ack, the "
            "advisory will no longer trigger startup banners. Run `shaggy "
            "doctor` first to see active advisories and their IDs."
        ),
    )
    doctor_parser.set_defaults(func=cmd_doctor)
