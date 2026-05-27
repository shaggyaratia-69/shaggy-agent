from pathlib import Path


def test_find_product_update_wheel_uses_shaggy_product_dir(monkeypatch, tmp_path):
    """Portable product installs can update from the copied product folder."""
    product = tmp_path / "Shaggy-Agent-Product"
    dist = product / "dist"
    dist.mkdir(parents=True)
    older = dist / "shaggy_agent-0.14.0-py3-none-any.whl"
    newer = dist / "shaggy_agent-0.15.0-py3-none-any.whl"
    older.write_text("old")
    newer.write_text("new")

    monkeypatch.setenv("SHAGGY_PRODUCT_DIR", str(product))

    from shaggy_cli.main import _find_product_update_wheel

    assert _find_product_update_wheel() == newer


def test_find_product_update_wheel_ignores_missing_env(monkeypatch):
    monkeypatch.delenv("SHAGGY_PRODUCT_DIR", raising=False)

    from shaggy_cli.main import _find_product_update_wheel

    assert _find_product_update_wheel() is None


def test_cmd_update_pip_installs_from_product_wheel(monkeypatch, tmp_path):
    """`shaggy update` should use the copied product folder before PyPI."""
    product = tmp_path / "Shaggy-Agent-Product"
    dist = product / "dist"
    dist.mkdir(parents=True)
    wheel = dist / "shaggy_agent-0.15.0-py3-none-any.whl"
    wheel.write_text("wheel")
    calls = []

    monkeypatch.setenv("SHAGGY_PRODUCT_DIR", str(product))
    monkeypatch.setattr("shaggy_cli.main.shutil.which", lambda name: "/usr/local/bin/uv" if name == "uv" else None)
    monkeypatch.setattr("shaggy_cli.main.subprocess.run", lambda cmd: calls.append(cmd) or type("R", (), {"returncode": 0})())

    from shaggy_cli.main import _cmd_update_pip

    _cmd_update_pip(object())

    assert calls == [["/usr/local/bin/uv", "pip", "install", "--python", __import__("sys").executable, "--upgrade", str(wheel)]]
