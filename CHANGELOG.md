# Changelog

The skill and the `/api/v1` and MCP surface it runs on, by skill version. The API itself changes in place
with no compatibility window; a version here names the app build the skill was tested against.

## 0.1.17 — 2026-11-17

- The agent sets the period boundaries from the household's main income: each period ends on a
  posted payday (calendar months with no regular income), and onboarding confirms the choice
  instead of asking for a length.
- A household whose exports reach back past today's period starts with its last two or three
  complete periods built from them, one month at a time: stage, review and approve, `check_period`,
  `open_period`. Schedules and funds come after the first month.
- Staging into a period that has ended keeps only its rows (`dropped.after_period` counts the rest);
  `open_period` refuses while the closing period has unreviewed rows unless `discard_unreviewed`.
- `review_import` pages 20 rows at a time with up to three compact precedents per row; the agent
  follows `next_cursor` until it is null.

## 0.1.16 — 2026-11-17

- Onboarding asks which other bank accounts receive regular moves or hold fund money and proposes
  adding each as an account, created only on the member's yes; only an account with no moves, or
  one the member declines, stays untracked.
- A tracked account with no export (a savings account) is recorded from the other account's
  transfer rows; its interest shows as a small unaccounted figure at the close.

## 0.1.15 — 2026-11-17

- `get_context` → `setup` lists `currency` until the owner has chosen it; the agent asks even when
  the default looks right.
- `create_fund` requires a cap (an amount or a percent); there is no 100% default.
- Each member's cash account is named after them ("Petr cash"); an ambiguous account name answers
  with each candidate's member.
- Mapping an imported row to a kind against its bank line's direction is refused.
- The default categories have Housing in place of Rent.

## 0.1.14 — 2026-11-16

- The close says its balances open the next period and are not corrected afterwards; a wrong one
  shows as unaccounted at the next close.

## 0.1.13 — 2026-11-16

- A schedule's new amount starts at a payment or date the member picks (`amount_change_options`,
  `update_schedule` with `effective_from`); earlier payments keep the old amount, and the change can
  be undone until the first payment at the new amount (`undo_amount_change`).
- `correct_opening_balance` fixes an account's opening balance in the open period where it was first
  given.
- Statements are staged with the account each file is from, and a transfer row names the account it
  went to (`to_account`). `check_period` lists card payments still `in_transit`; the close passes
  the confirmed ones as pending instead of adjusting a balance by hand. Statements are exported on
  the period's last day.
- Archiving a category ends or moves its schedules, and an archived category can be restored.

## 0.1.12 — 2026-11-11

- Setting a household up moves from the app to the agent. The member signs up, starts the connection
  and creates or joins the household on the consent screen; the agent then sets the currency
  (`update_household`), adds each member's accounts (`create_account`), invites members
  (`invite_member`, only an address the owner gives), and opens the first period. `get_context` →
  `setup` says what is left.

## 0.1.11 — 2026-11-06

- "How did this fund get to its balance?" reads `get_fund_statement`: per period, the opening and
  closing balance and every row that moved the fund, including what a close paid in and money moved
  between funds.

## 0.1.10 — 2026-10-14

- Recording by hand no longer searches for duplicates first: the app refuses a likely match as
  `possible_duplicate`, with the rows waiting in review and the recorded transactions it may be.
  The skill records the waiting row, or updates the recorded one, instead.

## 0.1.9 — 2026-10-11

- The overview names the three kinds of schedule: bills, budgets and income.

## 0.1.8 — 2026-10-11

- "Who owes whom" reads `get_settlement` instead of computing it by hand: the app's money custody
  (`custody: by_keeper`, a keeper per fund) gives the transfers, and `drift` says when the funds and
  the accounts disagree; `absorb_drift` books it. Under `pooled` the skill offers custody.
- A period close reports the settlement it leaves (`check_period`'s `settlement`).

## 0.1.7 — 2026-10-11

- A schedule's `mode` is `bill` or `budget` (formerly `fixed` and `spread`; `flexible` is gone),
  on every tool and in the period routine.

## 0.1.6 — 2026-10-11

- An agent that drives a browser fetches the bank exports itself once the member signs in;
  `references/banks.md` names each bank's online banking and the BMO card's missing pending rows.
- `get_context`'s `skill.version` is read as the oldest skill the app works with: a newer skill
  runs without a warning, so a skill-only release needs no app change.

## 0.1.5 — 2026-10-08

- A row set aside in an earlier batch stages set aside again, with its comment
  (`guess_source: set_aside`), instead of returning to review.
- `approve_import` takes `schedule_item_id`, the row `schedule_create` or `schedule_patch` belongs
  to, so a new schedule can start from one row of an approve that records several.

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
