# The period routine

Once per period, per household. Each step names its tool and what to read in the answer. The
direct-API equivalent of every tool is in [api.md](api.md).

## 0. Orient

`get_context` → the current period's dates, the members, your scope. `read_notes` → the
household's conventions. `list_accounts` → each member's accounts (`is_credit`, `is_cash`) and
the notes' mapping of each to its bank accounts.

A period's last day is also the next one's first, so a row dated that day belongs to whichever
period was open when it was recorded. Find a period's rows by its id (`find_transactions` with
the period), never by date.

Stop here if the token is `read`: the routine writes.

## 1. Get the exports

One CSV per bank account per member, covering the current period from its first day (rows before
it are dropped as out of period; a row the bank posted after the period's end is next period's).
The bank's own download, unchanged — [banks.md](banks.md) says which banks and how. A member
hands you the files, or you fetch them where the notes say they are kept.

## 2. Stage

`stage_statement` with `member` and the member's files as `{name, content}`; `include_pending`
when the member wants pending card rows recorded now (they come back as `(pending)` in the bank
text). One batch per member; a batch is scoped to one member.

Read the answer:

- `statements[]` — each file's detected format and row count. A file the parser refused is not
  staged: see banks.md § When a file is refused.
- `dropped.out_of_period` — rows before the period; expected.
- Rows set aside in an earlier batch stage `ignored` again (`guess_source: set_aside`), with that
  batch's comment. Undo one only when the member says it is a transaction after all.
- Rows the app settled: `duplicate` (already in the ledger by hand), a `transfer` pair (two
  rows moving the same money between the member's own accounts), a bill match
  (`occurrence_id` set). These need nothing from you.
- `review_count` — what step 3 is about.

## 3. Review

`review_import` with the batch → every row a person must decide: date, amount, direction, bank
text, and `precedents` (the household's past transactions for the same merchant, this member
first, newest first, up to ten, each with its destination, the `schedule` it drew on — `mode`
`spread` is a budget, `fixed` a bill — or `unplanned`, and its comment) with a `precedent_summary`
by category and schedule, such as `Home · Groceries 5, Home · unplanned 2, fund Kids 3`.

A destination for a `spend` row is a category **and** its plan: the budget it draws on
(`schedule_id`), the bill it pays (`occurrence_id`), or `unplanned: true`. `approve_import` skips a
spend row that names none of the three. Precedents agree only when they agree on both.

Decide each row in this order; the first rule that applies wins:

| The row is… | Do |
|---|---|
| a move the notes say is not a transaction here — from an untracked account, a card payment from chequing, the deposit side of a member-to-member transfer, a row the member enters by hand | `map_import_rows` with `status: ignored` and a comment naming the reason |
| a payment of a bill the app did not match (amount differs from the plan, or paid late) — check `list_bills` with `status: unpaid` | map it with the bill's `occurrence_id`; the plan adjusts |
| a row whose precedents agree (two or more, one destination and plan, this member) | map it to that destination and plan; list it under "recorded from precedent" in your summary so the member can glance |
| a counterparty or merchant the notes settle (e.g. "e-transfers to J. Smith are rent") | map it as the notes say |
| a recurring charge with no schedule (a subscription, a new bill) | map it, and record it with `schedule_create` on the approve (`mode: fixed`, `frequency`, `interval`, `amount`, and `schedule_item_id` naming the row when the approve records several) so the next period expects it |
| anything else — precedents split (between categories, or between budgets or unplanned in one category), none, an unknown counterparty, an amount that matches nothing | a question for the member (SKILL.md § Asking the household), the choices naming the budget or unplanned |

Never choose from merchant text alone: the same store is Home one day and a child's fund the
next, and the app's `guess_source` stays `none` for a reason.

A `dedup_possible` row (a near match in the ledger outside the three-day window) is a question
only if the dates differ by more than a few days; otherwise confirm it as `status: duplicate`.
A pair the app proposed but the notes contradict: `not_a_transfer` on the row splits it.

Dedup compares one bank row with one ledger entry. A member's single hand entry for a purchase the
bank split into two charges (same merchant, same day, amounts summing to the entry) is not caught:
both rows come to review. Record the bank rows with the hand entry's comment and destination, then
`delete_transaction` the hand entry — with the member's yes, since it is their entry.

Send the questions. Apply the answers with `map_import_rows`; an answer you cannot map ("that was
for Mom") is a comment on the row, with the member's chosen destination.

## 4. Record

`approve_import` with the batch and the row ids (or the mappings riding along) and `dry_run`
first. Read `effects` per transaction: the period it lands in, the bill it settles and what
remains of it, an `overspent_amount` on a budget. Mapping a row can attach a bill to it; check
every row's `occurrence_id` against what the row is (a restaurant charge does not pay a streaming
bill) and clear a wrong one with `occurrence_id: null` — its schedule goes with it — before
approving. A `skipped` spend row named no plan: map its budget or `unplanned: true`. An effect the
member did not expect (a bill settled twice, a different period) is a question before the real
write.

Then the same call with a `request_id`. Rows that now match the ledger (the member entered them
meanwhile) are skipped, not duplicated.

`complete_import` when `review_count` is 0; it refuses while rows are pending, which is the
check. A batch you cannot finish stays open in the app's review screen for the member.

## 5. Check what is unrecorded

`check_period` with the period's dates and every account's closing balance as the bank shows it
on the period's last day (a credit account's balance is what is owed; cash accounts as the notes
say, usually 0). Balances come from the member or from the bank's account page.

- **Pending card charges.** When pending rows were recorded (`include_pending`), the card balance
  you enter is the bank's current balance **plus its pending total**: the bank leaves pending out,
  the ledger already has it. Otherwise the check is off by exactly the pending total, and a later
  error can hide it.
- **Running balances in an export** are not a closing balance: rows sharing a date can be printed
  in any order, so the last row's balance may be from before another row that day. Take the
  closing balance from the account page.

The answer is `unaccounted` per member: what their accounts moved that the books do not show.
Near zero for everyone → the period is ready. Otherwise, in this order:

1. The notes' balance convention — a Ninepigs account that stands for two bank accounts needs
   both balances folded in (the commonest cause).
2. A pending card row the bank has since posted, or a row posted after the export was taken:
   `find_transactions` for the amount. A gap equal to the card's pending total is a balance
   entered without pending (see Pending card charges above).
3. A hand entry with a typo (amount, direction, member), or a hand entry duplicating a bank row
   recorded by the import: `find_transactions` with the period and the member;
   `update_transaction` fixes it, `delete_transaction` removes a duplicate.
4. A cash expense nobody recorded: the member's call.

Report the figure per member and what explains it; do not open the period on a figure the member
has not accepted.

## 6. Close and open

`open_period` with the next period's dates (the household's period length is in the notes; the
new period starts the day the current one ends), the balances from step 5, `end_schedule_ids`
for schedules the member said to end, and a `request_id`. Run `check_period` once more when
anything changed since step 5: the real write answers only the new period, so the figures you
report come from that last check.

Report: the closed period's net, the distributions into funds, and the new period's dates.

## 7. Write back

`update_notes` with what the period taught and the member confirmed: a new counterparty, a
merchant whose destination is now settled, a balance convention, a bank quirk. Keep the
template's sections; replace an entry rather than appending a contradiction.

## The run's numbers

End with one table — it is the household's own measure of whether the routine is getting cheaper:

| Measure | This period |
|---|---|
| Rows staged | |
| Settled by the app (duplicates, pairs, bills) | |
| Rows reviewed | |
| Questions to members (of which multiple choice) | |
| Recorded | |
| Set aside | |
| Unaccounted per member at close | |
