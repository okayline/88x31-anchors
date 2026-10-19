# 88x31 cLuB ledger receipts

Every button made, traded, fused or found in [~*~ 88x31 cLuB ~*~](https://88x31.app) goes into
the cLuB's **ledger**: one long chain where each entry's fingerprint is built from the one before it.
Change any old entry and every fingerprint after it breaks.

That proves the chain hasn't been edited *since someone saved a copy of it*. This repo is that copy,
kept by someone the webmaster doesn't control: **Bitcoin**.

## What happens every hour

1. A GitHub Action asks 88x31.app for the ledger's newest fingerprint (the "head").
2. If it changed, the Action writes it into a small receipt in [`receipts/`](receipts/) and gets an
   [OpenTimestamps](https://opentimestamps.org) proof for it (the matching `.ots` file).
3. Within a few hours the proof gets locked into a Bitcoin block, and the Action swaps in the finished proof.
4. Every receipt gets a line in [`log.md`](log.md).

No crypto is bought, held or spent. OpenTimestamps is free and only uses Bitcoin as a notary nobody controls.

## Two ledgers

The same job also stamps the **shared item registry's** ledger (the numbered copies and their histories used by every game),
fetched from the dungeon-items Worker (`/api/registry/head`: entry count, newest fingerprint and copy count, nothing about who holds what).
Its receipts live in [`registry/`](registry/), with their own `log.md`. Checking works the same way.

## Checking a receipt yourself

- **Easy way:** go to [opentimestamps.org](https://opentimestamps.org), drop in a receipt's `.txt.ots`
  file and then its `.txt` file. It tells you the Bitcoin block and the time it proves.
- **Then:** compare the receipt's `head` with the ledger on 88x31.app (Fair Play → The Ledger).
  If the cLuB's ledger ever disagreed with a receipt from the past, its history was changed.

## What this can't prove

A receipt shows the ledger hasn't changed since that hour. It can't show every event was recorded
honestly in the first place. That's true of any blockchain.
