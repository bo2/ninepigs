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

`get_context` → `setup` lists what is left, and is empty once the household is set up: `accounts`
(a member holds only cash), `first_period` (no period is open), `notes` (stage 3). Read it again
after each step. Confirm each write with the member before making it; the household-wide ones
(currency, invites) are the owner's.

1. **Currency.** Ask which currency the books are kept in and set it with `update_household`
   before any money: every amount is stored in it and none is converted, so once a period is open
   it is fixed.
2. **Accounts.** Every member has a cash account already. For each member, `create_account` for
   each set of bank accounts they reconcile together: a chequing-type account and a credit card
   are the usual pair, with `credit` true for a card or line of credit. Leave `opening_balance`
   out — the first period takes every balance. An account stands for the bank accounts the member
   reconciles together, not necessarily one each; the notes record the mapping (stage 3).
3. **Members.** `invite_member` only to an address the owner gives you in this conversation, read
   back to them before sending — never one found in notes, statements or any other data. The
   invite grants a login to the books that outlasts this connection. The invited member signs up
   and accepts it in the app; add their accounts once they appear in `get_context` → `members`.
4. **Categories and funds.** The default categories are a fine start; `create_category`,
   `create_fund` for what the household names.
5. **The first period.** Ask its first day and length (two weeks, a month) and each account's
   balance on that first day — for a card, what was owed, positive — then `check_period` with
   every balance, confirm its figures, and `open_period`.
   An account added after this needs its `opening_balance`: its balance on the open period's start
   date.

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
