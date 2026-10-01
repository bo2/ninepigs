# The API directly

For an agent with no MCP client — a headless job, a cron run. `scripts/ninepigs.py` calls
`/api/v1` with the token from `NINEPIGS_API_TOKEN` (or the file `~/.config/ninepigs/token`);
Python 3, no dependencies. Every field and error code is at ninepigs.com/docs/api; read the one
endpoint you need there rather than the whole document.

```bash
scripts/ninepigs.py GET /me
scripts/ninepigs.py GET '/transactions?date_from=2026-09-01&kind=spend&limit=50'
scripts/ninepigs.py --dry-run POST /transactions '{"kind":"spend","amount":"42.10","date":"2026-09-14","comment":"groceries","category_id":3,"user_id":1}'
scripts/ninepigs.py --key groceries-2026-09-14-a POST /transactions '{…the same body…}'
scripts/ninepigs.py --form POST /import-batches user_id=2 include_pending=1 'files[]=@chequing.csv' 'files[]=@card.csv'
```

Conventions: `snake_case`; money as decimal strings in the household's currency, a transaction
`amount` positive with `kind` carrying the direction; dates `YYYY-MM-DD`; lists page by `cursor`
(`limit` up to 100); errors as `{"error": {"code", "message", "fields"?, "hint"?}}`; 60 calls a
minute per token (the script waits once on a 429). `--dry-run` adds `dry_run=true`, which runs the
write and rolls it back, answering `meta.effects`. `--key` sends an `Idempotency-Key`: the same
key and body within 24 hours replays the first answer instead of writing again.

## Each tool's call

| Tool | Call |
|---|---|
| `get_context` | `GET /me` — `user.id` is your `user_id`; `members`, `categories`, `funds` by id and name; `current_period`; `token.scope` |
| `read_notes`, `update_notes` | `GET /notes`, `PUT /notes` `{"content": "…"}` |
| `list_accounts` | `GET /accounts` |
| `stage_statement` | `--form POST /import-batches` with `user_id`, `include_pending`, `source=agent`, `files[]=@…` |
| `review_import` | `GET /import-batches/{id}/items?needs=review` — each row with `precedents` and `precedent_summary` |
| `map_import_rows` | `PATCH /import-batches/{id}/items` `{"items": [{"id", "kind"?, "category_id"?, "fund_id"?, "to_user_id"?, "occurrence_id"?, "comment"?, "status"?}]}` (`write` scope) — or let the mappings ride along on the approve, which `record` allows |
| `approve_import` | `POST /import-batches/{id}/approve` `{"items": [...]}` or `{"item_ids": [...]}`, plus `schedule_create` / `schedule_patch`, `force`; `--dry-run` first, then `--key` |
| `complete_import`, `discard_import` | `POST /import-batches/{id}/complete`, `DELETE /import-batches/{id}` |
| `list_imports` | `GET /import-batches`, `?status=reviewed` for finished ones |
| `not_a_transfer` | `POST /import-batches/{id}/items/{item}/not-a-transfer` |
| `check_period` | `--dry-run POST /periods` `{"start_date", "end_date", "balances": [{"account_id", "amount"}, …every account]}` → `meta.effects.unaccounted` per member |
| `open_period` | the same body with `--key`, plus `pending_transaction_ids`, `end_schedule_ids` |
| `list_bills` | `GET /occurrences?status=due` and `status=overdue`; `GET /occurrences/matches?amount=…&date=…&text=…` ranks the bills a payment could settle |
| `settle_bill` | `POST /occurrences/{id}/settle` (`amount`, `date`, `comment`, `user_id` optional) |
| `record_transaction` | `POST /transactions`; several at once `POST /transactions/batch` `{"transactions": [...]}` up to 50 |
| `update_transaction`, `delete_transaction` | `PATCH /transactions/{id}`, `DELETE /transactions/{id}` |
| `find_transactions` | `GET /transactions?search=…&date_from=…&user_id=…&kind=…&status=unplanned\|overspent` |
| `summarize_spending` | `GET /transactions/summary?date_from=…&date_to=…&group_by=category\|member\|month\|kind` |
| `get_budget_status` | `GET /periods/current/budget` — "how much is left" is `totals.spending.redistributed.remaining` |
| `list_schedules`, `create_schedule`, `update_schedule` | `GET /schedules`, `POST /schedules`, `PATCH /schedules/{id}` (`end_date` ends one) |
| `get_fund_status`, `create_fund`, `update_fund`, `close_fund`, `transfer_between_funds` | `GET /funds`, `POST /funds`, `PATCH /funds/{id}`, `POST /funds/{id}/close` `{"move_to_fund_id"}`, `POST /funds/transfers` |
| `create_category` | `POST /categories` |
| what changed | `GET /activity?since=…&api_token_id=…` |

## Errors worth knowing

| Code | Meaning | Do |
|---|---|---|
| `unauthenticated` 401 | token revoked or expired | a new token from the app |
| `token_read_only`, `token_record_only` 403 | the scope does not reach this call | say which scope it needs |
| `token_forbidden_route` 403 | the path is outside `/api/v1` | fix the path |
| `household_required` 409 | the account has no household | onboarding stage 1 |
| `conflict` 409 | the books refuse the write; the message names what to resolve (a batch with pending rows, a fund with a balance) | resolve it first |
| `validation_failed` 422 | `error.fields` names each bad field | fix the body |
| `idempotency_conflict` 422 | the key was used with a different body | a new key for a new write |
| `rate_limited` 429 | over 60 a minute | the script waits once; slow a loop down |
