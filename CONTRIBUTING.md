# Contributing to Nexus CLI

## Git Flow

We use [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/):

```
main        ← Producción (stable releases)
  └── dev   ← Integración (trabajo activo)
        ├── feature/init-command
        ├── feature/server-setup
        └── fix/update-path
```

### Rules

1. **Nunca commit directo a `main`** — solo merges desde `dev` con PR aprobado
2. **Trabaja en `dev` o en branches `feature/*`** desde `dev`
3. **PRs a `dev`** requieren review antes de merge
4. **Releases**: `dev` → PR → `main` con tag semver (v0.2.0)

### Branch naming

- `feature/description` — nueva funcionalidad
- `fix/description` — corrección de bug
- `refactor/description` — refactorización
- `docs/description` — documentación

### Commits

Usa [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add init command for project scaffolding
fix: handle missing pyproject.toml in update
refactor: remove install/uninstall (moved to erp-nexus)
docs: update README with new CLI scope
test: add tests for server setup generation
```

## Development setup

```bash
# Clone
git clone https://github.com/ERPNexusGroup/nexus.git
cd nexus
git checkout dev

# Install dependencies
uv sync

# Run tests
uv run pytest
```

## Pull Request checklist

- [ ] Tests pasan (`uv run pytest`)
- [ ] CHANGELOG.md actualizado
- [ ] Convención de commits seguida
- [ ] Documentación actualizada si aplica
