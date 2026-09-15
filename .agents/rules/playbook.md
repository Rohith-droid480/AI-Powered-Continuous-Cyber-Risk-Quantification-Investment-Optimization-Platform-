# Project Playbook & Milestone Reporting Protocol

## Layer Milestone Reports
- At the completion of each layer (Layer 1 through 6), a milestone report must be generated in `reports/`.
- Reports must adhere to `MILESTONE_REPORT_TEMPLATE.md`.
- End every milestone response with: `ROUTE THIS REPORT → [Target Role/Session]` per §3 routing table.

## Database Architecture Disclosure
Layer 2 uses SQLite (app.db) for the internal-round demo, a deliberate deviation from the originally planned PostgreSQL, chosen for zero-dependency demo reliability (no external DB service to fail during judging). Schema and query logic are portable to PostgreSQL without architecture changes if needed for the full SIH round.

