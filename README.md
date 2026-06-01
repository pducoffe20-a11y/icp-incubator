# ICP Incubator

ICP Incubator turns a raw account list into a practical seller workflow: account fit, why-now signals, buyer angles, short briefs, and review-ready first-touch drafts.

This started as Pat's Account Outreach Pipeline for D2L Brightspace association, credentialing, continuing education, and member-training prospecting. The goal is not to mass-blast. The goal is to make account selection and outreach sharper, more honest, and faster to review.

## What it does

```text
account-list.csv
  -> intake + data QA
  -> ICP fit + signal review
  -> account brief
  -> Pat-voice first touch
  -> drafts.json for Outlook review folder
```

## Core rule

Nothing sends automatically. ICP Incubator creates reviewed sales assets and staged drafts only.

## Quick start

Run validation:

```bash
make validate
```

Run the sample pipeline:

```bash
make run-sample
```

Run against a real account list:

```bash
python3 scripts/run_pipeline.py path/to/accounts.csv --outbox outbox
python3 scripts/validate_drafts_json.py outbox/drafts.json
```

Stage the drafts in Outlook on Windows desktop Outlook:

```powershell
pwsh ./scripts/create_outlook_drafts.ps1 -DraftsFile ./outbox/drafts.json -FolderName "Outreach - Review"
```

## Workflow

1. Intake the CSV and split accounts into Ready and Hold.
2. Score ICP fit using vertical, persona, use case, signal, and evidence strength.
3. Build one short account brief per Ready account.
4. Write one specific, low-pressure first-touch email.
5. Assemble `outbox/drafts.json` for Outlook staging.
6. Flag thin evidence, missing contacts, or inferred fields for review.

## Repo map

| Path | Purpose |
|---|---|
| `AGENTS.md` | Master agent operating instructions. |
| `CODEX.md` | Notes for coding-agent execution. |
| `pipeline/` | Step-by-step operating playbooks. |
| `reference/` | ICP rules, voice profile, CSV schema, D2L angles. |
| `templates/` | Account brief and drafts JSON schemas. |
| `scripts/` | Validation helpers. |
| `scripts/run_pipeline.py` | Runnable CSV-to-briefs-and-drafts pipeline. |
| `scripts/create_outlook_drafts.ps1` | Local Outlook staging script. |
| `examples/` | Sample account list, brief, and drafts payload. |
| `config/` | User-editable settings. |
| `outbox/` | Generated briefs and drafts. Git-ignore in real repo. |
| `docs/` | Build notes and future design docs. |

## Evidence model

`Strong` means the CSV includes a specific why-now signal. `Thin` means the account has a plausible fit from vertical or persona but no signal. `None` means the row has no usable training, education, credentialing, compliance, workforce, or member-learning clue. Thin and None drafts are marked `"review": true`.

## GitHub readiness

The repo includes a GitHub Actions workflow at `.github/workflows/validate.yml`. It runs `make validate` and `make run-sample` on push and pull request.

## Current status

This is v0.2 rebuild scaffolding: runnable local pipeline, validation, sample tests, Outlook staging script, and GitHub CI. It still intentionally avoids automatic sending and live enrichment.
