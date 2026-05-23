from argparse import Namespace

from shaggy_cli.doctor import resolve_doctor_fix_mode


def test_shaggy_doctor_defaults_to_auto_repair():
    """Bare `shaggy doctor` should attempt safe repairs by default."""
    assert resolve_doctor_fix_mode(Namespace()) is True


def test_shaggy_doctor_can_be_forced_to_check_only():
    """`shaggy doctor --no-fix` / --check should preserve diagnosis-only mode."""
    assert resolve_doctor_fix_mode(Namespace(fix=True, no_fix=True)) is False
    assert resolve_doctor_fix_mode(Namespace(fix=True, check=True)) is False


def test_shaggy_doctor_keeps_legacy_fix_flag_true():
    assert resolve_doctor_fix_mode(Namespace(fix=True)) is True
