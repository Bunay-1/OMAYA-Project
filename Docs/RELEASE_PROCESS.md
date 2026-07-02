# Release Process

OMAYA Platform uses semantic versioning and automated release notes generation to ensure consistent, auditable delivery.

## Versioning

- `MAJOR.MINOR.PATCH` follows semantic versioning.
- Breaking changes increment the MAJOR.
- New features increment the MINOR.
- Bug fixes and documentation changes increment the PATCH.

## Release automation

- GitHub Actions `release.yml` is configured to run `release-please` on pushes to `main`.
- This workflow updates `CHANGELOG.md` and creates GitHub releases automatically.
- `dependabot.yml` keeps dependencies up to date for npm, pip, GitHub Actions and Docker images.

## Branch strategy

- `main` is the release branch.
- Feature branches should use `feature/<topic>`.
- Bugfix branches should use `fix/<topic>`.
- Release candidates should use `release/<version>`.

## Pull request requirements

- Tests must pass in CI.
- Linting must pass.
- Changes must be documented in `CHANGELOG.md` or through the release automation workflow.
