#!/usr/bin/env python3
"""Hourly receipts for two ledgers: the 88x31 cLuB ledger and the shared item registry's ledger.

For each ledger:
1. Ask its server for the current head (the latest fingerprint) and entry count.
2. If the head changed since the last receipt, write it to <receipts>/<time>.txt and get an
   OpenTimestamps proof for that file (<receipts>/<time>.txt.ots).
3. Finish any proofs from the last few days that are still waiting on Bitcoin.
4. Add one line per new receipt to the ledger's log.

If one ledger can't be reached or reports a broken chain, the other is still stamped and the run
fails at the end, so GitHub emails the owner.

The GitHub Action commits whatever changed. Nothing here needs a password or a key.
"""
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OTS = os.environ.get("OTS", "ots")
UPGRADE_DAYS = 3


class Ledger:
    def __init__(self, title, url, folder):
        self.title = title
        self.url = url
        base = os.path.join(HERE, folder) if folder else HERE
        self.receipts = os.path.join(base, "receipts")
        self.log = os.path.join(base, "log.md")
        self.last = os.path.join(base, "last-head.txt")


LEDGERS = [
    Ledger("88x31 cLuB", os.environ.get("LEDGER_URL", "https://88x31.app/api/ledger?limit=1"), ""),
    Ledger("Shared item registry", os.environ.get("REGISTRY_URL", "https://88x31.app/api/registry/head"), "registry"),
]


def fetch_head(url):
    req = urllib.request.Request(url, headers={"user-agent": "88x31-anchors (GitHub Action)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("ok") is False:
        # Fail loudly: GitHub emails the repo owner when a scheduled run fails.
        sys.exit(f"The ledger at {url} reports its chain is BROKEN at entry {data.get('broken_at')}. No receipt made.")
    head = str(data.get("head") or "")
    if len(head) != 64 or any(c not in "0123456789abcdef" for c in head):
        sys.exit(f"Unexpected head from {url}: {head!r}")
    return head, int(data.get("entries") or 0)


def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def stamp(L, now):
    head, entries = fetch_head(L.url)
    if head == read(L.last):
        print(f"{L.title}: head unchanged ({head[:12]}…), no new receipt.")
        return
    os.makedirs(L.receipts, exist_ok=True)
    name = now.strftime("%Y-%m-%dT%H-%M-%SZ") + ".txt"
    path = os.path.join(L.receipts, name)
    with open(path, "w") as f:
        f.write(f"{L.title} ledger receipt\n"
                f"time:    {now.strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"entries: {entries}\n"
                f"head:    {head}\n"
                "check:   chain ok\n")
    subprocess.run([OTS, "stamp", path], check=True)
    with open(L.last, "w") as f:
        f.write(head + "\n")
    new_log = not os.path.exists(L.log)
    with open(L.log, "a") as f:
        if new_log:
            f.write(f"# {L.title} ledger receipts\n\n"
                    "One line per hour the ledger changed. Times are UTC. Each line's proof is in receipts/.\n\n"
                    "| time (UTC) | entries | head | receipt |\n|---|---|---|---|\n")
        f.write(f"| {now.strftime('%Y-%m-%d %H:%M')} | {entries} | `{head}` | [{name}](receipts/{name}) |\n")
    print(f"{L.title}: new receipt {name}: entry {entries}, head {head[:12]}…")


def upgrade(L, now):
    """Swap the waiting proofs from the last few days for finished, Bitcoin-confirmed ones."""
    if not os.path.isdir(L.receipts):
        return
    cutoff = (now - timedelta(days=UPGRADE_DAYS)).strftime("%Y-%m-%dT%H-%M-%SZ")
    recent = sorted(os.path.join(L.receipts, n) for n in os.listdir(L.receipts)
                    if n.endswith(".txt.ots") and n >= cutoff)
    for p in recent:
        # A proof still waiting on Bitcoin makes `ots upgrade` fail; that's normal, try again next hour.
        r = subprocess.run([OTS, "upgrade", p], capture_output=True, text=True)
        print(f"{os.path.basename(p)}: {'done' if r.returncode == 0 else 'still waiting'}")
    for bak in os.listdir(L.receipts):
        if bak.endswith(".bak"):
            os.remove(os.path.join(L.receipts, bak))


if __name__ == "__main__":
    now = datetime.now(timezone.utc)
    failed = []
    for L in LEDGERS:
        try:
            stamp(L, now)
        except (Exception, SystemExit) as e:
            print(f"{L.title}: FAILED: {e}")
            failed.append(L.title)
        upgrade(L, now)
    if failed:
        sys.exit("Failed: " + ", ".join(failed))
