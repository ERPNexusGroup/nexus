# Changelog

All notable changes to Nexus CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] — 2026-04-01

### Changed
- CLI completely restructured as bootstrap/deploy tool
- Removed SDK dependency (no longer needed)
- Removed catalog, registry, storage modules (moved to erp-nexus)

### Added
- `nexus init` — Project scaffolding with manage.py, pyproject.toml, .env, README
  - `--with-docker` for docker-compose.yml + Dockerfile
  - `--with-git` for git init
- `nexus server setup` — Generate gunicorn.conf.py, nginx.conf, systemd service
- `nexus server start/stop/restart/status` — Server control
- `nexus update [--check]` — ERP core updater
- `nexus doctor` — Environment dependency checker
- `nexus info` — Project status display
- 9 tests passing

### Removed
- `create`, `validate`, `install`, `uninstall`, `catalog`, `registry` commands
- catalog.py, registry.py, storage/filesystem.py
- SDK dependency

## [0.1.0] — 2026-03-12

### Added
- CLI with Click framework
- `create` command for module scaffolding
- `validate` command with AST parser
- `install` / `uninstall` with transactional rollback
- `catalog` commands (list, info, update)
- `registry` management (add, remove, list, export, import)
- `list` and `info` commands for installed components
- Rich console output with panels and tables
- Config file support (~/.nexus/config.json)

[Unreleased]: https://github.com/ERPNexusGroup/nexus/compare/v0.1.0...dev
[0.1.0]: https://github.com/ERPNexusGroup/nexus/releases/tag/v0.1.0
