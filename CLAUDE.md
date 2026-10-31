# 88x31-anchors: working notes

## This repo

Public repo of hourly Bitcoin timestamps (OpenTimestamps) for two ledgers: the 88x31 cLuB ledger and the shared item registry's ledger. A receipt shows the ledger hasn't changed since that hour. The README explains how anyone can check one.

**How it works**
- The GitHub Action `.github/workflows/stamp.yml` runs `stamp.py` at 17 past every hour, or on demand with "Run workflow".
- `stamp.py` asks club.88x31.app for each ledger's newest head. If the head changed, it writes a receipt in `receipts/` (the registry's go in `registry/receipts/`) and gets an OpenTimestamps proof (`.ots`) for it. It then finishes any proofs from the last 3 days that were waiting on Bitcoin, and adds one line per new receipt to that ledger's `log.md`.
- The Action commits and pushes to `main` itself, with the message "Receipt YYYY-MM-DD HH:MM UTC".
- If one ledger can't be reached or reports a broken chain, the other is still stamped and the run fails at the end, so GitHub emails kura.

**Rules for this repo**
- The receipts are the evidence. Never edit, rename, delete or regenerate anything in `receipts/`, `registry/`, `log.md` or `last-head.txt` by hand. Only `stamp.py` and the Action write them.
- The Action pushes every hour, so fetch and rebase before any push of yours.
- Times here are UTC (receipts, `log.md`, commit messages), not HST.
- Nothing here uses a key or password. Don't add one.
- There are no tests, version numbers or changelog. `log.md` is the record. If the process changes, update the README, because people use it to verify receipts.
- `__pycache__/stamp.cpython-313.pyc` is committed and there is no `.gitignore`. That looks accidental; leave it unless kura asks.
