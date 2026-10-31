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

<!-- BEGIN SHARED RULES v7 (2026-10-31). One copy of this block is in every Dungeons repo's CLAUDE.md. The source is dungeon-notes/SHARED-RULES.md. Don't edit the block inside a repo: change the source, then copy it into every repo. -->
## Working rules (shared by every repo)

"kura" is the owner. "4Dungeon" is the repo `daily-dungeon`. Other Claude chats work in these repos and share no memory with you: the repo and its changelog are the shared record. A repo section above beats a rule below, except rules 1 to 4.

**Honesty (never broken)**
1. Never lie. State as fact only what you opened, read or ran this turn; the rest is "not checked", or isn't said. Label opinions "my opinion". "Should work" and "probably" count as not checked.
2. Answers about code or data end with "Not checked:".
3. Check first, then reply once. If you were wrong, the first sentence says what you said, what is true, and the source.
4. Never say something was done, pushed or fixed unless you saw it succeed. Report failures plainly.

**Searching**
5. Before saying "no", or recommending something new, search the chat (if you can reach it), every repo you can reach, and the live state. Say what you searched and what you found. Say "I couldn't find it", never "that isn't true". If kura remembers something you can't find, don't call kura wrong, and don't state it as fact.

**Design**
6. Give honest answers, including "this isn't worth building". Give one recommendation. Never tell kura to playtest the game.
7. Before proposing, name the goal it serves (4Dungeon: `dungeon-notes/daily-dungeon-design.md`, section 15) and how it would most likely fail. No goal, no proposal. Propose the smallest version first.

**Building**
8. Commit locally as asked. Push only when kura says to. "Push" means: commit everything that's changed and push it all to `main` (in repos that deploy from `main`, that is also the release).
9. Don't add anything kura didn't ask for (a button, a screen, a page, a feature), change tables or scheduled tasks, or add a dependency: ask first.
10. Delete, don't park: no new flags or "off for now" code. Fix a shared problem once, in the shared place. Prefer changing what exists to adding a file. Each changelog line says what was removed as well as what was added.
11. No new secrets (passwords, tokens, keys such as `DAILY_SECRET`) in files, commits or replies. If you find one already committed, tell kura, and don't repeat it.

**Working with kura**
12. Don't act without kura's explicit permission. A question gets an answer, not an action: "Can you remove that rule?" is a request; "What happens if we remove that rule?" is a question. If you can't tell which, answer, then ask "want me to do it?" and wait. Reading and searching to find the answer is fine.
13. Disagree before building, not after. Silence means "not now": raise each item once.

**Defaults**
- Testing takes 2 to 3 minutes in total, with no edge cases. A repo's required check (such as `npm test`) counts toward that. Need more? Ask first.
- Times are Hawaii time (HST) unless a file says otherwise (88x31-anchors receipts are UTC).
- Some repos get automated commits: fetch before you push.
<!-- END SHARED RULES v7 -->
