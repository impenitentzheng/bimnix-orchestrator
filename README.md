# BIMNIX Orchestration Layer v1

Runnable MVP for the BIMNIX Social Pipeline using owner-by-exception.

This project does not assume that Claude, NotebookLM, Gemini, DeepSeek, Perplexity, GitHub, or Meta/Instagram APIs are connected. Unverified capabilities are represented explicitly and route to exception states instead of silently pretending to work.

## Quick Start

```powershell
git clone https://github.com/impenitentzheng/bimnix-orchestrator.git
cd bimnix-orchestrator
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m bimnix_orchestrator.cli init-db
python -m bimnix_orchestrator.cli emit-social-event --title "Revit QA automation" --claim "Automated checks can reduce manual BIM QA work." --source "https://example.com/source"
```

Use the returned event `id`:

```powershell
python -m bimnix_orchestrator.cli run-once <event-id>
python -m bimnix_orchestrator.cli list-events
```

## MVP Behavior

- source-free claims stop at `CLAIM_REQUIRES_APPROVAL`
- unverified NotebookLM/Claude/Gemini/DeepSeek capabilities stop or fall back conservatively
- official Meta/Instagram publishing is blocked until capability verification
- every state transition is appended to SQLite for audit trail

## GitHub PR Workflow

Work through pull requests:

1. Create a branch for integration or pipeline changes.
2. Update `config/capabilities.example.toml` only after capability verification.
3. Run tests locally.
4. Open a PR and let `.github/workflows/ci.yml` run.
5. Merge only after review.

## Next Integrations To Verify

- GitHub repository and PR permissions
- official Meta/Instagram publishing path for the BIMNIX account
- source-grounded NotebookLM export or API capability
- Claude technical-review invocation path
- Gemini media generation and Google Drive handoff
- Perplexity discovery API or export path
- DeepSeek batch generation API path

## Docs

- `docs/ARCHITECTURE.md`
- `docs/OWNER_BY_EXCEPTION.md`
- `docs/PR_RUNBOOK.md`
