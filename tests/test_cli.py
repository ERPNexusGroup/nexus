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


def test_install_missing_dependency(tmp_path: Path) -> None:
    base = tmp_path / "components"
    base.mkdir()

    comp_a = base / "core_auth"
    comp_b = base / "core_users"
    comp_a.mkdir()
    comp_b.mkdir()

    _write_meta(comp_a, name="core_auth")
    # core_users depends on core_auth, but we will install only core_users
    _write_meta(comp_b, name="core_users")
    (comp_b / "__meta__.py").write_text(
        (comp_b / "__meta__.py").read_text(encoding="utf-8")
        + 'depends = ["core_auth"]\n',
        encoding="utf-8",
    )

    install_base = tmp_path / "installed"
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["install", str(comp_b), "--install-path", str(install_base)],
    )
    assert result.exit_code == 1


def test_catalog_stub(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        '{"items":[{"technical_name":"core_auth","description":"Auth core","versions":[{"version":"0.1.0","source":"https://example.com"}]}]}',
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["catalog", "list", "--source", str(catalog)],
    )
    assert result.exit_code == 0
    assert "core_auth" in result.output


def test_catalog_update_stub(tmp_path: Path) -> None:
    runner = CliRunner()
    out = tmp_path / "catalog.json"
    result = runner.invoke(
        cli,
        ["catalog", "update", "--output", str(out)],
    )
    assert result.exit_code == 0
    assert out.exists()


def test_install_from_catalog_with_package_map(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        '{"items":[{"technical_name":"core_auth","description":"Auth core","versions":[{"version":"0.1.0","source":"https://example.com"}]}]}',
        encoding="utf-8",
    )

    pkg = tmp_path / "core_auth"
    pkg.mkdir()
    _write_meta(pkg, name="core_auth")

    install_base = tmp_path / "installed"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "install",
            "catalog:core_auth",
            "--catalog-source",
            str(catalog),
            "--package",
            f"core_auth={pkg}",
            "--install-path",
            str(install_base),
        ],
    )
    assert result.exit_code == 0
    assert (install_base / "core_auth").exists()


def test_install_from_catalog_download(tmp_path: Path) -> None:
    # create a local zip package
    pkg_dir = tmp_path / "core_auth"
    pkg_dir.mkdir()
    _write_meta(pkg_dir, name="core_auth")
    zip_path = tmp_path / "core_auth.zip"
    import zipfile
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(pkg_dir / "__meta__.py", arcname="core_auth/__meta__.py")

    zip_url = "file:///" + zip_path.as_posix()
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        f'{{"items":[{{"technical_name":"core_auth","description":"Auth core","versions":[{{"version":"0.1.0","source":"{zip_url}"}}]}}]}}',
        encoding="utf-8",
    )

    install_base = tmp_path / "installed"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "install",
            "catalog:core_auth",
            "--catalog-source",
            str(catalog),
            "--install-path",
            str(install_base),
        ],
    )
    assert result.exit_code == 0
    assert (install_base / "core_auth").exists()
