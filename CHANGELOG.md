# Changelog

All notable changes to Nexus CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased] — dev branch

### Changed
- Refocus as bootstrap/deploy/server tool (not module management)
- Module management moved to erp-nexus (manage.py commands)
- Module creation moved to sdk-nexus
- Updated README with new scope

### Planned
- `nexus init` — Project scaffolding
- `nexus server setup` — Production config generation
- `nexus server start/stop/restart` — Server control
- `nexus update` — ERP core updater
- `nexus doctor` — Environment checker

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
