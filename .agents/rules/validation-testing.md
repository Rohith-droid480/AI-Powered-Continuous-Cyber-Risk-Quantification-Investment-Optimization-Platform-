# Validation & Testing Guidelines

## Testing Mandates
- **Backend Tests**: All schemas, API endpoints, risk formulas, simulation loops, and optimization algorithms must be unit-tested via `pytest` in `app/tests/`.
- **Reproducibility**: Vectorized Monte Carlo seeds must be controllable for deterministic unit testing.
- **Budget Compliance**: Optimization outputs must strictly satisfy $\sum \text{Cost}_k \cdot x_k \le \text{Budget}$.
- **Frontend Verification**: UI components must compile cleanly with `npx vite build` and maintain schema alignment with backend API stubs.
