# Onboarding a household

Three stages. `get_context` tells you which one the household is at.

## Stage 1 — the household exists in the app

Done in the app at ninepigs.com, not through the API:

1. Sign up, verify the email, create the household (its name and currency) or join one from an
   invitation.
2. Invite the other members.
3. Add each member's accounts: a chequing-type account and a credit card are the usual pair, plus
   a cash account if the member spends cash. An account stands for the bank accounts the member
   reconciles together, not necessarily one each — the notes record the mapping (stage 3).
4. Set the categories (the defaults are a fine start) and the funds.
5. Open the first period with each account's current balance.

A call that answers `household_required` means step 1 is not done; `get_context` with no
`current_period` means step 5 is not. Send the member to the app for these; you cannot create
them.

## Stage 2 — the connection

A token from the app (Settings → Security → API tokens: name it after the agent, pick the scope,
copy it once) or an OAuth connection from a hosted agent's connector settings. `record` runs the
import and records money; `write` also keeps notes, schedules and funds and opens periods.
The install steps per agent are at ninepigs.com/docs/connect.

`get_context` answers with the token's name, scope and expiry when the connection works.

## Stage 3 — learn the household

The notes are empty, so ask — one message, every question in it, with the household's own
names from `get_context` filled in:

1. **Accounts.** For each Ninepigs account: which bank account(s) does it stand for, and at
   which bank? Any bank account you do not track at all (a savings account whose moves should be
   ignored)?
2. **Entry habits.** Who enters spending by hand during the period, and who relies on the
   import? For hand-entry members the import is mostly a reconciliation; for the others it is
   the main entry path.
3. **Counterparties.** The people you e-transfer with regularly, and what those transfers are
   (rent, a loan, a shared bill, a gift).
4. **Funds.** What each fund is for, and whether a particular store or site is always one
   member's or one fund's spending.
5. **The period.** Its length (two weeks, a month), and what cash accounts close at.
6. **Exports.** Where the bank CSVs come from each period, or whether a member hands them over.

Write the answers into the notes in the template's shape ([notes-template.md](notes-template.md))
with `update_notes`, read them back to the member, and fix what they correct.

Then run the first import ([period-routine.md](period-routine.md)). With no precedents every
row the app cannot settle is a question; group them per member as multiple choice from the
categories and funds, and record what they answer. That period's answers are the next period's
precedents — the second import is mostly confirmations.
