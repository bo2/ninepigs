# Changelog

The skill and the `/api/v1` and MCP surface it runs on, by skill version. The API itself changes in place
with no compatibility window; a version here names the app build the skill was tested against.

## 0.1.0 — 2026-10-01

First release.

- The skill: the period routine (export, stage, review, record, check, close), the triage policy,
  how to ask the household, money questions, keeping schedules, budgets and funds current, onboarding
  a household from nothing, household notes.
- MCP tools it is written against: `get_context`, `read_notes`, `update_notes`, `list_accounts`,
  `stage_statement`, `review_import`, `map_import_rows`, `approve_import`, `complete_import`,
  `discard_import`, `list_imports`, `not_a_transfer`, `check_period`, `open_period`, plus the
  existing transaction, bill, budget, fund and schedule tools.
- `scripts/ninepigs.py`, the dependency-free client for agents without an MCP connection.
