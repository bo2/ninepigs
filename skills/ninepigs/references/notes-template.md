# Household notes — template

The notes are one markdown document the app keeps per household (`read_notes`, `update_notes`).
Keep these sections, in this order; drop one that is empty. Facts only, each one something the
app cannot infer; no tokens, passwords or private remarks. An entry that no longer holds is
replaced, not appended to.

```markdown
# Household notes

## Accounts
- Admin's **Chequing** = Big Bank chequing ****1234 plus the linked savings ****5678 (its moves to chequing are internal; fold both balances in at close).
- Admin's **Credit card** = Big Bank Mastercard. Payments to it from chequing are not transactions.
- Alice's **Chequing** = Other Bank chequing. Her savings ****9012 is untracked: ignore its moves.
- Cash accounts close at 0 unless the member says otherwise.

## Members
- Admin enters nothing by hand; the import is the entry path.
- Alice enters most spending by hand during the period; the import is a reconciliation.

## Counterparties
- e-transfer to J. SMITH — rent, Admin, Housing (bill "Rent").
- e-transfer from K. LEE — Alice's share of the car, income.
- e-transfer to M. BROWN — a loan (loan out); the repayments come back as loan in.

## Merchants
- DOLLAR STORE — Home, unless the member says it was for the kids (fund Kids).
- AMZN Mktp — ask; it is everything.
- STREAMCO — bill "Streaming", Admin.

## Period
- Two weeks, 1st and 16th. Admin closes it; Alice sends her balances the evening before.
- Exports: both members download CSVs from their bank's site; Alice's card export carries an extra trailing column the app accepts.

## Open
- Whether Alice's savings should become a tracked account (asked 2026-10-01).
```
