#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path

REQUIRED_HEADERS = [
    "account_name", "contact_name", "contact_title", "contact_email",
    "website", "vertical", "state", "signal", "priority"
]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def main(path: str) -> int:
    p = Path(path)
    if not p.exists():
        print(f"ERROR: missing file: {p}")
        return 2
    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = [h for h in REQUIRED_HEADERS if h not in headers]
        if missing:
            print("ERROR: missing headers: " + ", ".join(missing))
            return 1
        ready = []
        hold = []
        for i, row in enumerate(reader, start=2):
            account = (row.get("account_name") or "").strip()
            email = (row.get("contact_email") or "").strip().lower()
            if not account:
                hold.append((i, account or "<blank>", "missing account_name"))
            elif not email:
                hold.append((i, account, "missing contact_email"))
            elif not EMAIL_RE.match(email):
                hold.append((i, account, "invalid contact_email"))
            else:
                ready.append((i, account, email))
    print(f"Ready: {len(ready)}")
    print(f"Hold: {len(hold)}")
    for line, account, reason in hold:
        print(f"HOLD line {line}: {account} — {reason}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_csv.py <accounts.csv>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
