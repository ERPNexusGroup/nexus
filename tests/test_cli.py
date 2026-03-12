import sys
from pathlib import Path

from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from nexus.cli import cli  # noqa: E402


def _write_meta(component_dir: Path, *, name: str) -> None:
    content = (
        f'technical_name = "{name}"\n'
        f'display_name = "{name.replace("_", " ").title()}"\n'
        'component_type = "module"\n'
        'package_type = "extension"\n'
        'python = ">=3.11"\n'
        'erp_version = ">=0.1.0"\n'
        'version = "0.1.0"\n'
    )
    (component_dir / "__meta__.py").write_text(content, encoding="utf-8")


def test_create_minimal(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["create", "demo_module", "--type=module", "--minimal", "--path", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert (tmp_path / "demo_module" / "__meta__.py").exists()


def test_validate_success(tmp_path: Path) -> None:
    component_dir = tmp_path / "demo_module"
    component_dir.mkdir()
    _write_meta(component_dir, name="demo_module")

    runner = CliRunner()
    result = runner.invoke(cli, ["validate", str(component_dir)])
    assert result.exit_code == 0


def test_install_uninstall_and_list(tmp_path: Path) -> None:
    component_dir = tmp_path / "demo_module"
    component_dir.mkdir()
    _write_meta(component_dir, name="demo_module")

    install_base = tmp_path / "installed"
    runner = CliRunner()

    install_result = runner.invoke(
        cli,
        ["install", str(component_dir), "--install-path", str(install_base)],
    )
    assert install_result.exit_code == 0
    assert (install_base / "demo_module").exists()

    list_result = runner.invoke(
        cli,
        ["list", "--install-path", str(install_base)],
    )
    assert list_result.exit_code == 0
    assert "demo_module" in list_result.output

    info_result = runner.invoke(
        cli,
        ["info", "demo_module", "--install-path", str(install_base)],
    )
    assert info_result.exit_code == 0
    assert "demo_module" in info_result.output

    uninstall_result = runner.invoke(
        cli,
        ["uninstall", "demo_module", "--install-path", str(install_base)],
    )
    assert uninstall_result.exit_code == 0
    assert not (install_base / "demo_module").exists()


def test_install_dry_run_and_registry_export_import(tmp_path: Path) -> None:
    component_dir = tmp_path / "demo_module"
    component_dir.mkdir()
    _write_meta(component_dir, name="demo_module")

    install_base = tmp_path / "installed"
    runner = CliRunner()

    dry_run = runner.invoke(
        cli,
        ["install", str(component_dir), "--install-path", str(install_base), "--dry-run"],
    )
    assert dry_run.exit_code == 0
    assert not (install_base / "demo_module").exists()

    install_result = runner.invoke(
        cli,
        ["install", str(component_dir), "--install-path", str(install_base)],
    )
    assert install_result.exit_code == 0

    export_path = tmp_path / "registry-export.json"
    export_result = runner.invoke(
        cli,
        ["registry", "export", "--output", str(export_path), "--install-path", str(install_base)],
    )
    assert export_result.exit_code == 0
    assert export_path.exists()

    uninstall_result = runner.invoke(
        cli,
        ["uninstall", "demo_module", "--install-path", str(install_base)],
    )
    assert uninstall_result.exit_code == 0

    import_result = runner.invoke(
        cli,
        ["registry", "import", "--input", str(export_path), "--install-path", str(install_base)],
    )
    assert import_result.exit_code == 0

    list_result = runner.invoke(
        cli,
        ["list", "--install-path", str(install_base)],
    )
    assert list_result.exit_code == 0
    assert "demo_module" in list_result.output
