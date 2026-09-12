# Model Prompting Guide

## Core Directives
- **Schema Contracts**: Strictly build against `app/schemas/models.py`.
- **No Masking**: Never suppress errors or use dummy try/except fallbacks without tracing root causes.
- **Empirical Verification**: Always run `pytest` and `npx vite build` to verify fixes before completing turns.
