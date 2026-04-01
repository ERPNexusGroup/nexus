"""Tests para nexus CLI."""
import sys
from pathlib import Path
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nexus.cli import cli


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "ERP Nexus" in result.output

    def test_version(self):
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "nexus" in result.output.lower()

    def test_doctor(self):
        result = self.runner.invoke(cli, ["doctor"])
        assert result.exit_code == 0
        assert "Python" in result.output

    def test_info(self):
        result = self.runner.invoke(cli, ["info"])
        assert result.exit_code == 0
        assert "Nexus CLI" in result.output

    def test_init_help(self):
        result = self.runner.invoke(cli, ["init", "--help"])
        assert result.exit_code == 0
        assert "proyecto" in result.output.lower()

    def test_server_help(self):
        result = self.runner.invoke(cli, ["server", "--help"])
        assert result.exit_code == 0
        assert "servidor" in result.output.lower()


class TestInit:
    def setup_method(self):
        self.runner = CliRunner()

    def test_creates_project(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["init", "test-project"])
            assert result.exit_code == 0
            assert Path("test-project/manage.py").exists()
            assert Path("test-project/pyproject.toml").exists()
            assert Path("test-project/modules").is_dir()
            assert Path("test-project/.env.example").exists()
            assert Path("test-project/.gitignore").exists()

    def test_with_docker(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["init", "test-docker", "--with-docker"])
            assert result.exit_code == 0
            assert Path("test-docker/docker-compose.yml").exists()
            assert Path("test-docker/Dockerfile").exists()

    def test_fails_if_exists(self):
        with self.runner.isolated_filesystem():
            Path("existing").mkdir()
            result = self.runner.invoke(cli, ["init", "existing"])
            assert result.exit_code == 1
