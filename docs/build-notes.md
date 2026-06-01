# ICP Incubator Build Notes

## v0.2 rebuild

- Adds `scripts/run_pipeline.py` as a dependency-free local runner.
- Adds `scripts/create_outlook_drafts.ps1` for Windows desktop Outlook staging.
- Adds unit tests and a GitHub Actions validation workflow.
- Uses `python3` in the Makefile for macOS compatibility.
- Keeps generated briefs and draft JSON out of Git with `outbox/` ignore rules.

## Safety choices

- The pipeline never sends email.
- The runner only uses CSV evidence; it does not browse or enrich.
- Missing or invalid email addresses are held.
- Drafts without strong evidence are marked `review:true`.

## Next build ideas

1. Add optional public-web research with source capture.
2. Add CRM/M365 enrichment behind explicit connectors.
3. Add JSON Schema validation from `templates/drafts.schema.json` if a schema library is allowed.
4. Add a richer config loader for `config/settings.yaml`.
5. Add approved D2L customer-story snippets by vertical.
