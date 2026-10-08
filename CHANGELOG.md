# Changelog

The skill and the `/api/v1` and MCP surface it runs on, by skill version. The API itself changes in place
with no compatibility window; a version here names the app build the skill was tested against.

## 0.1.4 — 2026-10-08

- Import review: a spend row is recorded only once it names its budget (`schedule_id`), its bill
  (`occurrence_id`) or `unplanned: true`; precedents and their summary show the schedule each one
  drew on, and the member's choices name the budget or unplanned.
- `map_import_rows` and `approve_import` take `unplanned`; clearing a wrong bill's
  `occurrence_id` clears its schedule too. `record_transaction` and `update_transaction` take
  `schedule_id` for a budget.

## 0.1.3 — 2026-10-05

- The period routine: a row on the boundary day belongs to the period open when it was recorded,
  so rows are found by period, not date; a hand entry for a purchase the bank split in two is not
  deduplicated and is resolved by hand; every mapped row's bill is checked before approving.
- The check: a card balance includes its pending total when pending rows were recorded; closing
  balances come from the account page, not an export's running balance.
- Writing: look for an imported row before recording spending by hand.
- Money questions: working out who owes whom when members keep personal funds.

## 0.1.2 — 2026-10-03

- `agents/openai.yaml`: Codex shows the skill under its own name and offers to connect the
  Ninepigs MCP server when it is missing.

## 0.1.1 — 2026-10-01

- A real `open_period` answers only the new period; the routine reports the figures from the last
  `check_period`. A refused statement file fails the `stage_statement` call naming the file.

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
