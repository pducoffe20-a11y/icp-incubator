# Codex build notes

This repository is designed to be run by an AI coding agent such as Codex.

## Start here

1. Read `AGENTS.md` completely.
2. Follow the pipeline files in order:
   - `pipeline/00-intake.md`
   - `pipeline/01-research.md`
   - `pipeline/02-messaging.md`
   - `pipeline/03-draft-emails.md`
   - `pipeline/04-qa.md`
3. Never send email. Produce `outbox/drafts.json` only.
4. Hand the user the PowerShell command in the final summary.

## Expected user task

The normal prompt is:

```text
Run the outreach pipeline on examples/sample-accounts.csv
```

For a real run, replace the sample CSV path with the uploaded account list.

## Build / validation checks

Run these before handoff:

```bash
make validate
make run-sample
```

To process a real CSV:

```bash
python3 scripts/run_pipeline.py path/to/accounts.csv --outbox outbox
python3 scripts/validate_drafts_json.py outbox/drafts.json
```

The Outlook draft creation step runs on Windows with desktop Outlook:

```powershell
pwsh ./scripts/create_outlook_drafts.ps1 -DraftsFile ./outbox/drafts.json -FolderName "Outreach - Review"
```
