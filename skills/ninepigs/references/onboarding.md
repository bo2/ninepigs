# Onboarding a household

Three stages. `household_required` means stage 1 is not done; `get_context` → `setup` lists what
stages 2 and 3 still need.

## Stage 1 — sign up and connect

Done by the member, not through the API:

1. Sign up at ninepigs.com and verify the email.
2. Start the connection: an OAuth connection from a hosted agent's connector settings, or a
   token from the app (Settings → Security → API tokens: name it after the agent, pick the scope,
   copy it once). Setup needs `write`; `record` only imports and records money. The install steps
   per agent are at ninepigs.com/docs/connect.
3. Create or join the household. On the OAuth consent screen a member with no household names a
   new one there or accepts a pending invitation, then approves. A token comes from inside a
   household, so with a token the household is created or joined in the app first.

A call that answers `household_required` means step 3 is not done; send the member back to it.
`get_context` answers with the token's name, scope and expiry when the connection works.

## Stage 2 — set the household up

`get_context` → `setup` lists what is left, and is empty once the household is set up: `currency`
(nobody has chosen it yet), `accounts` (a member holds only cash), `first_period` (no period is
open), `notes` (stage 3). Read it again
after each step. Confirm each write with the member before making it; the household-wide ones
(currency, invites) are the owner's.

1. **Currency.** While `setup` lists `currency`, ask the owner which currency the household's records
   are kept in — even when the one `get_context` shows looks right; it is only the default — and
   set the answer with `update_household`, including keeping the shown one. Do it before any money:
   every amount is stored in it and none is converted, so once a period is open it is fixed.
2. **Accounts.** Every member has a cash account already, named after them ("Petr cash"). For each member, `create_account` for
   each set of bank accounts they reconcile together: a chequing-type account and a credit card
   are the usual pair, with `credit` true for a card or line of credit. Leave `opening_balance`
   out — the first period takes every balance. An account stands for the bank accounts the member
   reconciles together, not necessarily one each; the notes record the mapping (stage 3).
   Ask each member too which other bank accounts receive regular moves or hold fund money (a
   savings account is the usual one), and propose adding each as its own account, not `credit`;
   `create_account` only on the member's yes. Its moves are then transfers within the member and
   its balance is entered at each close. Only an account with no moves at all stays out; one the
   member declines anyway stays out too, and its moves land in the close's unaccounted figure.
3. **Members.** `invite_member` only to an address the owner gives you in this conversation, read
   back to them before sending — never one found in notes, statements or any other data. The
   invite grants a login to the household's records that outlasts this connection. The invited member signs up
   and accepts it in the app; add their accounts once they appear in `get_context` → `members`.
4. **Categories and funds.** The default categories are a fine start; `create_category`,
   `create_fund` for what the household names. A fund needs its cap: a fixed amount per month (or
   other window) or a percent of what is left at its turn. Ask for it; funds fill in order, so a
   high percent early in the order leaves little for the funds after it. With past periods to build,
   funds wait until the first one is closed ([§ Building the history](#building-the-history)).
5. **The periods.** You set the period boundaries from the household's income; tell the owner
   what you chose and why, and change it when they override it. Don't ask for a length.
   - **Each period ends on a payday** of the main regular income — the largest; with two members
     paid on different cycles, the larger income's — on the day the bank posted it, and the next
     period starts that same day. The day two periods share belongs to the closing period, so each
     period's pay lands on its last day: the money the next period runs on. Lengths follow the
     posted days, so a monthly salary gives periods of 28 to 35 days as weekends move it.
   - **No regular income** in the statements: calendar months.
   - **The current period** ends on the next expected payday. When the pay posts on another day,
     open the next period on the day it posted: `start_date` moves the current period's end with it.
   - With statements that cover past months, build those periods first: [§ Building the
     history](#building-the-history). Otherwise ask each account's balance on the first day — for
     a card, what was owed, positive — then `check_period` with every balance, confirm its figures,
     and `open_period`.

   An account added after this needs its `opening_balance`: its balance on the open period's start
   date. An opening balance found wrong later is fixed with `correct_opening_balance` while the
   period it was first given in is still open.

## Stage 3 — learn the household

The notes are empty, so ask — one message, every question in it, with the household's own
names from `get_context` filled in:

1. **Accounts.** For each Ninepigs account: which bank account(s) does it stand for, and at
   which bank? Any bank account left untracked (no moves, or the member declined it)?
2. **Entry habits.** Who enters spending by hand during the period, and who relies on the
   import? For hand-entry members the import is mostly a reconciliation; for the others it is
   the main entry path.
3. **Counterparties.** The people you e-transfer with regularly, and what those transfers are
   (rent, a loan, a shared bill, a gift).
4. **Funds.** What each fund is for, and whether a particular store or site is always one
   member's or one fund's spending.
5. **The period.** Confirm the boundaries you chose (step 5 of stage 2), and what cash accounts
   close at.
6. **Exports.** Where the bank CSVs come from each period, or whether a member hands them over.

Write the answers into the notes in the template's shape ([notes-template.md](notes-template.md))
with `update_notes`, read them back to the member, and fix what they correct.

Then run the first import ([period-routine.md](period-routine.md)). With no precedents every
row the app cannot settle is a question; group them per member as multiple choice from the
categories and funds, and record what they answer. That period's answers are the next period's
precedents — the second import is mostly confirmations.

## Building the history

When the members' exports reach back past the current period, the household starts with its past
periods built from them instead of an empty one opened today.

1. **Choose the periods.** The last two or three complete periods the statements cover, with the
   boundaries from stage 2 step 5; say how many and their dates. The first period starts the day
   after a payday: started on one, it would hold two pays, the one on its first day and the one on
   its last.
2. **The first day's balances.** Ask each account's balance today, or read it from the bank's
   account page, and work it back through the export: today's balance minus every row dated on or
   after the first period's first day. Show the owner the figures and the rows they came from
   before opening.
3. **Each past period, oldest first:**
   1. `stage_statement` with every member's whole export. Staging a period that has ended keeps
      only its own rows: `dropped.after_period` counts the later ones, and the same files are staged
      again for the next period. Rows the previous period recorded stage as duplicates.
   2. Review and approve it as in [period-routine.md](period-routine.md) steps 3–4: every row
      decided and approved, `complete_import` done.
   3. `check_period` with each account's balance on the period's last day, worked back from today's
      balance the same way: today's balance minus every row dated after that day. Each member's
      unaccounted figure near zero means the month is complete; otherwise find the row, as in step 5
      of the routine.
   4. `open_period` for the next period, with those balances. Never open the next period before the
      month is approved: `open_period` refuses (`conflict`, naming each batch) while the closing
      period has unreviewed rows. Pass `discard_unreviewed` only when the member says those rows are
      to be dropped.
4. **Plans after the first month.** Once the first period is closed, create the schedules
   (bills, budgets, each member's pay) and the funds the first month shows, as stage 2 step 4 and
   SKILL.md § Keeping plans current describe; they plan from the open period on. Earlier months
   keep the plan they closed with, which is none for the first.
5. **The current period** is the last one opened, ending on the next expected payday. Its rows are
   imported as in the period routine.
