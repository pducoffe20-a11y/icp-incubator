#!/usr/bin/env python3
"""Run ICP Incubator from a CSV into account briefs and draft JSON.

The runner intentionally uses only CSV-provided evidence. It does not browse,
enrich, or send email. Rows with missing or invalid recipients are held.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_HEADERS = [
    "account_name",
    "contact_name",
    "contact_title",
    "contact_email",
    "website",
    "vertical",
    "state",
    "signal",
    "priority",
]

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SLUG_RE = re.compile(r"[^a-z0-9]+")

D2L_ANGLES = {
    "association": "member education, CE, certificates, and professional development in one place, with cleaner reporting",
    "healthcare": "CE programs across member hospitals, chapters, or professional groups",
    "credentialing": "completion tracking, renewal cycles, and learner progress without turning reporting into a manual project",
    "ce": "completion tracking, renewal cycles, and learner progress without turning reporting into a manual project",
    "banking": "education and compliance teams proving completion clearly when regulators, boards, or member institutions ask",
    "manufacturing": "workforce training, onboarding, and upskilling across plants, partners, or member companies",
    "workforce": "workforce training, onboarding, and upskilling across plants, partners, or member companies",
}

PAIN_BY_VERTICAL = {
    "healthcare": "completion tracking across member groups can get manual fast",
    "banking": "completion proof can be hard to pull cleanly when someone asks",
    "manufacturing": "training records can get scattered across sites and teams",
    "association": "member-learning reporting can turn into a lot of manual follow-up",
    "credentialing": "renewal and completion records can be painful to reconcile",
    "ce": "renewal and completion records can be painful to reconcile",
    "workforce": "training progress can be hard to see across cohorts and locations",
}


@dataclass(frozen=True)
class AccountRow:
    line: int
    account_name: str
    contact_name: str
    contact_title: str
    contact_email: str
    website: str
    vertical: str
    state: str
    signal: str
    priority: str


@dataclass(frozen=True)
class HoldRow:
    line: int
    account: str
    reason: str


def clean(value: str | None) -> str:
    return " ".join((value or "").strip().split())


def slugify(value: str) -> str:
    slug = SLUG_RE.sub("-", value.lower()).strip("-")
    return slug or "account"


def load_accounts(path: Path) -> tuple[list[AccountRow], list[HoldRow]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = [header for header in REQUIRED_HEADERS if header not in headers]
        if missing:
            raise ValueError("missing headers: " + ", ".join(missing))

        ready: list[AccountRow] = []
        hold: list[HoldRow] = []
        for line, raw in enumerate(reader, start=2):
            row = AccountRow(
                line=line,
                account_name=clean(raw.get("account_name")),
                contact_name=clean(raw.get("contact_name")),
                contact_title=clean(raw.get("contact_title")),
                contact_email=clean(raw.get("contact_email")).lower(),
                website=clean(raw.get("website")),
                vertical=clean(raw.get("vertical")).lower(),
                state=clean(raw.get("state")),
                signal=clean(raw.get("signal")),
                priority=clean(raw.get("priority")).lower(),
            )
            if not row.account_name:
                hold.append(HoldRow(line, "<blank>", "missing account_name"))
            elif not row.contact_email:
                hold.append(HoldRow(line, row.account_name, "missing contact_email"))
            elif not EMAIL_RE.match(row.contact_email):
                hold.append(HoldRow(line, row.account_name, "invalid contact_email"))
            else:
                ready.append(row)
    return ready, hold


def account_initials(account: str) -> str:
    words = [w for w in re.split(r"[^A-Za-z0-9]+", account) if w]
    initials = "".join(w[0].upper() for w in words if w[0].isalpha())
    return initials if 2 <= len(initials) <= 5 else account.split()[0]


def first_name(contact_name: str) -> str:
    return contact_name.split()[0] if contact_name else "there"


def evidence_for(row: AccountRow) -> str:
    if row.signal:
        return "Strong"
    if row.vertical or row.contact_title:
        return "Thin"
    return "None"


def vertical_key(row: AccountRow) -> str:
    text = f"{row.vertical} {row.contact_title}".lower()
    for key in D2L_ANGLES:
        if key in text:
            return key
    return "association"


def d2l_angle(row: AccountRow) -> str:
    return D2L_ANGLES[vertical_key(row)]


def likely_pain(row: AccountRow) -> str:
    key = vertical_key(row)
    if row.signal:
        return PAIN_BY_VERTICAL.get(key, "tracking and reporting can get harder as the program grows")
    return "needs research"


def why_now(row: AccountRow) -> str:
    return f"{row.signal} (from CSV signal)" if row.signal else "needs research"


def subject_for(row: AccountRow) -> str:
    if row.signal:
        return f"{account_initials(row.account_name)} training - quick thought"
    return f"{account_initials(row.account_name)} member learning - quick question"


def opener_for(row: AccountRow) -> str:
    if row.signal:
        return f"Saw the note about {row.signal[0].lower() + row.signal[1:] if row.signal else row.signal}."
    if row.contact_title:
        return f"I noticed your work around {row.contact_title.lower()} at {row.account_name}."
    return f"I had {row.account_name} on my list because of the member-learning fit."


def draft_for(row: AccountRow) -> dict[str, object]:
    evidence = evidence_for(row)
    review = evidence != "Strong"
    angle = d2l_angle(row)
    pain = likely_pain(row)
    if evidence == "Strong":
        body = (
            f"Hi {first_name(row.contact_name)},\n\n"
            f"{opener_for(row)} That usually means {pain}.\n\n"
            f"Brightspace is often a fit when teams need {angle}.\n\n"
            "Worth a quick chat sometime? No pressure either way.\n\n"
            "Pat"
        )
    else:
        body = (
            f"Hi {first_name(row.contact_name)},\n\n"
            f"{opener_for(row)} I do not want to assume the current priorities from the outside, "
            "but it looked close enough to ask.\n\n"
            f"Brightspace may be useful if {row.account_name} is trying to support {angle}.\n\n"
            "Curious if this is on your radar. No pressure either way.\n\n"
            "Pat"
        )

    return {
        "account": row.account_name,
        "to": row.contact_email,
        "to_name": row.contact_name,
        "subject": subject_for(row),
        "body": body,
        "body_format": "text",
        "category": "Outreach Pipeline",
        "review": review,
        "evidence": evidence,
    }


def brief_for(row: AccountRow) -> str:
    evidence = evidence_for(row)
    recipient = f"{row.contact_name} - {row.contact_email}" if row.contact_name else row.contact_email
    sources = "CSV signal field" if row.signal else "CSV account metadata only"
    return "\n".join(
        [
            f"# Account Brief - {row.account_name}",
            "",
            f"- **Bucket:** {row.vertical or 'needs research'}",
            f"- **Best persona:** {row.contact_title or 'needs research'}",
            f"- **Why now:** {why_now(row)}",
            f"- **Likely pain:** {likely_pain(row)}",
            f"- **D2L angle:** {d2l_angle(row)}",
            "- **Customer story match:** No close match found",
            f"- **Evidence:** {evidence}",
            f"- **Recipient:** {recipient}",
            f"- **Sources used:** {sources}",
            "",
            "**Read for the writer:** Keep the note honest and short. Do not imply a pain point beyond the listed evidence.",
            "",
        ]
    )


def write_outputs(rows: Iterable[AccountRow], outbox: Path) -> list[dict[str, object]]:
    briefs_dir = outbox / "briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)

    drafts: list[dict[str, object]] = []
    for row in rows:
        (briefs_dir / f"{slugify(row.account_name)}.md").write_text(brief_for(row), encoding="utf-8")
        drafts.append(draft_for(row))

    outbox.mkdir(parents=True, exist_ok=True)
    (outbox / "drafts.json").write_text(json.dumps(drafts, indent=2) + "\n", encoding="utf-8")
    return drafts


def run(input_csv: Path, outbox: Path, hold_if_no_signal: bool) -> int:
    ready, hold = load_accounts(input_csv)
    if hold_if_no_signal:
        kept: list[AccountRow] = []
        for row in ready:
            if evidence_for(row) == "None":
                hold.append(HoldRow(row.line, row.account_name, "missing signal"))
            else:
                kept.append(row)
        ready = kept

    drafts = write_outputs(ready, outbox)
    flagged = sum(1 for draft in drafts if draft["review"])

    print(f"Drafted: {len(drafts)} emails -> {outbox / 'drafts.json'}")
    print(f"Held for review: {len(hold)} accounts")
    for item in hold:
        print(f"- line {item.line}: {item.account} ({item.reason})")
    print(f"Flagged in-draft: {flagged} emails")
    print()
    print("Run this to stage drafts in Outlook:")
    print(f"  pwsh ./scripts/create_outlook_drafts.ps1 -DraftsFile {outbox / 'drafts.json'} -FolderName \"Outreach - Review\"")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ICP Incubator briefs and Outlook draft JSON.")
    parser.add_argument("input_csv", type=Path, help="Account CSV to process.")
    parser.add_argument("--outbox", type=Path, default=Path("outbox"), help="Output directory for briefs and drafts.")
    parser.add_argument(
        "--hold-if-no-signal",
        action="store_true",
        help="Hold rows without a why-now signal instead of creating review-flagged drafts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return run(args.input_csv, args.outbox, args.hold_if_no_signal)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
