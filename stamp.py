#!/usr/bin/env python3
"""Hourly receipt for the 88x31 cLuB ledger.

1. Ask 88x31.app for the ledger's current head (the latest fingerprint) and entry count.
2. If the head changed since the last receipt, write it to receipts/<time>.txt and get an
   OpenTimestamps proof for that file (receipts/<time>.txt.ots).
3. Finish any proofs from the last few days that are still waiting on Bitcoin.
4. Add one line per new receipt to log.md.

The GitHub Action commits whatever changed. Nothing here needs a password or a key.
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

LEDGER_URL = os.environ.get("LEDGER_URL", "https://88x31.app/api/ledger?limit=1")
OTS = os.environ.get("OTS", "ots")
HERE = os.path.dirname(os.path.abspath(__file__))
RECEIPTS = os.path.join(HERE, "receipts")
LOG = os.path.join(HERE, "log.md")
LAST = os.path.join(HERE, "last-head.txt")
UPGRADE_DAYS = 3


def fetch_head():
    req = urllib.request.Request(LEDGER_URL, headers={"user-agent": "88x31-anchors (GitHub Action)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("ok") is False:
        # Fail loudly: GitHub emails the repo owner when a scheduled run fails.
        sys.exit(f"The ledger reports its chain is BROKEN at entry {data.get('broken_at')}. No receipt made.")
    head = str(data.get("head") or "")
    if len(head) != 64 or any(c not in "0123456789abcdef" for c in head):
        sys.exit(f"Unexpected head from the ledger: {head!r}")
    return head, int(data.get("entries") or 0)


def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def stamp(now):
    head, entries = fetch_head()
    if head == read(LAST):
        print(f"Head unchanged ({head[:12]}…), no new receipt.")
        return
    os.makedirs(RECEIPTS, exist_ok=True)
    name = now.strftime("%Y-%m-%dT%H-%M-%SZ") + ".txt"
    path = os.path.join(RECEIPTS, name)
    with open(path, "w") as f:
        f.write("88x31 cLuB ledger receipt\n"
                f"time:    {now.strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"entries: {entries}\n"
                f"head:    {head}\n"
                "check:   chain ok\n")
    subprocess.run([OTS, "stamp", path], check=True)
    with open(LAST, "w") as f:
        f.write(head + "\n")
    new_log = not os.path.exists(LOG)
    with open(LOG, "a") as f:
        if new_log:
            f.write("# 88x31 ledger receipts\n\n"
                    "One line per hour the ledger changed. Times are UTC. Each line's proof is in receipts/.\n\n"
                    "| time (UTC) | entries | head | receipt |\n|---|---|---|---|\n")
        f.write(f"| {now.strftime('%Y-%m-%d %H:%M')} | {entries} | `{head}` | [{name}](receipts/{name}) |\n")
    print(f"New receipt {name}: entry {entries}, head {head[:12]}…")


def upgrade(now):
    """Swap the waiting proofs from the last few days for finished, Bitcoin-confirmed ones."""
    if not os.path.isdir(RECEIPTS):
        return
    cutoff = (now - timedelta(days=UPGRADE_DAYS)).strftime("%Y-%m-%dT%H-%M-%SZ")
    recent = sorted(os.path.join(RECEIPTS, n) for n in os.listdir(RECEIPTS)
                    if n.endswith(".txt.ots") and n >= cutoff)
    for p in recent:
        # A proof still waiting on Bitcoin makes `ots upgrade` fail; that's normal, try again next hour.
        r = subprocess.run([OTS, "upgrade", p], capture_output=True, text=True)
        print(f"{os.path.basename(p)}: {'done' if r.returncode == 0 else 'still waiting'}")
    for bak in os.listdir(RECEIPTS):
        if bak.endswith(".bak"):
            os.remove(os.path.join(RECEIPTS, bak))


if __name__ == "__main__":
    now = datetime.now(timezone.utc)
    stamp(now)
    upgrade(now)
