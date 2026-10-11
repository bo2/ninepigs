# Bank exports

The import reads the banks' own CSV downloads, unchanged. One file is one account.

## Supported formats

| Bank, account | Header the parser recognizes | Notes |
|---|---|---|
| BMO chequing | `First Bank Card, Transaction Type, Date Posted, Transaction Amount, Description` | negative amount = spend |
| BMO credit card | `Item #, Card #, Transaction Date, Posting Date, Transaction Amount, Description` | positive amount = spend; `Card #` tells cards on one statement apart |
| Scotiabank chequing | `Filter, Date, Description, Sub-description, Type of Transaction, Amount, Balance` | the running `Balance` can be out of order within a day; take the closing balance from the account page |
| Scotiabank credit card | `Filter, Date, Description, Sub-description, Status, Type of Transaction, Amount` | `Status` marks rows the bank has not posted yet; they are skipped unless `include_pending` |

A known header matches as a prefix, so a bank adding a trailing column does not break the file.

## Getting the file

From the bank's online banking, the account's transaction list, "download" or "export" as CSV,
for a date range starting on the period's first day (rows before it are dropped anyway; rows
after the period's end belong to the next one). Pending card rows are included by the bank's
export when it offers them; the app records them only with `include_pending`.

**When you drive a browser, fetch the files yourself.** Open each bank's online banking, ask the
member to sign in — never type a member's credentials — and download every account's CSV. On a
second import in the same period, start from the day the last export ended; skip an account
with no new rows.

| Bank | Online banking | Quirk |
|---|---|---|
| BMO | `https://www1.bmo.com/banking/digital/accounts` | the credit card export leaves out pending rows: read them from the card's page and record them with `record_transaction` |
| Scotiabank | `https://secure.scotiabank.com/accounts` | |

**Otherwise** — no browser, or no member present to sign in (a scheduled run) — the member hands
you the files in the conversation, or the notes say where they keep them.

## When a file is refused

`stage_statement` fails as `validation_failed` naming the file the parser could not read, and
nothing is staged. Then:

1. Check the header against the table: a renamed column means the bank changed its export, and
   the app's parser needs to learn it — tell the member, so it gets fixed in the app rather than
   worked around every period.
2. A bank not in the table is not supported yet. Do not transcribe its rows into one of the
   known formats from memory; the member can rewrite the export into one of the headers above
   (date, amount with the sign convention, description) if they want it imported now, and the
   bank is a request for the app.
