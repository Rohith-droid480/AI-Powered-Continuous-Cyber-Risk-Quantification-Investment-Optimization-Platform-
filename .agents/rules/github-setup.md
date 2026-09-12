# GitHub Workflow & Branching Conventions

## Repository Strategy
- **`main` Branch**: Locked production branch. Only the initial setup commit is permitted directly on `main`.
- **Feature Branches**: All subsequent layer features must be developed on feature branches (e.g. `feature/layer-1-ingestion`, `feature/layer-4-simulation`).
- **Pull Requests**: Code is merged into `main` via PRs after automated tests pass and milestone reports are created.
