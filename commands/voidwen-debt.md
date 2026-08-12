---
description: Harvest deferred voidwen: shortcuts into a ledger.
---

Collect every deliberate simplification marked with a `voidwen:` comment into one
ledger.

Run: `grep -rn "voidwen:" . --include=*.py --include=*.js --include=*.ts --include=*.sh --include=*.css`
(add extensions as needed; skip `node_modules` and generated dirs).

For each hit, print a table row:

| file:line | ceiling (the corner cut) | upgrade path | trigger |
|---|---|---|---|

Extract the ceiling and upgrade path from the comment text. The trigger is the
condition in the comment ("if throughput exceeds 100 req/s", "when the table
exceeds 10k rows"). Sort by how close each trigger is to being hit, if known.

This is a read-only report. It does not resolve or edit any shortcut.
