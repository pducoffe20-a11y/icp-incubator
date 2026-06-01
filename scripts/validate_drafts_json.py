#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

REQUIRED = ["account", "to", "subject", "body", "body_format", "category", "review", "evidence"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_EVIDENCE = {"Strong", "Thin", "None"}


def main(path: str) -> int:
    p = Path(path)
    if not p.exists():
        print(f"ERROR: missing file: {p}")
        return 2
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("ERROR: root must be a JSON array")
        return 1
    errors = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"item {idx}: must be object")
            continue
        for key in REQUIRED:
            if key not in item:
                errors.append(f"item {idx}: missing {key}")
        if "to" in item and not EMAIL_RE.match(str(item["to"])):
            errors.append(f"item {idx}: invalid to email")
        if item.get("evidence") not in VALID_EVIDENCE:
            errors.append(f"item {idx}: invalid evidence")
        if item.get("body_format") not in {"text", "html"}:
            errors.append(f"item {idx}: invalid body_format")
    if errors:
        print("ERRORS:")
        for e in errors:
            print("- " + e)
        return 1
    print(f"OK: {len(data)} drafts")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_drafts_json.py <drafts.json>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
