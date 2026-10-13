# BIMNIX Orchestration Layer v1

## Goal

The MVP removes the owner from copy-paste coordination. The owner is called only for exceptions, approvals, business DMs, copyright risk, unverified technical claims, and publishing failures.

Target owner time: <=30 minutes per week after real integrations are verified and connected.

## Operating Principle

No integration is assumed available. Every external AI or publishing tool must be represented in `config/capabilities.example.toml` and marked verified before the pipeline routes automated work to it.

## Shared State and Event Bus

Shared state is an append-only SQLite event log:

- every event has `id`, `parent_id`, `state`, `route_to`, `exception_reason`, and `payload`
- state changes create a new event instead of mutating the previous event
- this gives auditability for GitHub PR review and later production operations

## Social Pipeline

1. Knowledge/Technical Event
2. Evidence
3. Source/Credit verification
4. Content candidate
5. Editorial decision
6. Media
7. QC
8. Publish gate
9. Instagram/Meta publishing where officially supported
10. Insights
11. Learning loop

## Routing

- ChatGPT: orchestration, editorial decision, source/credit policy, owner summaries
- Codex: automation, event bus, tests, logging, GitHub PR preparation
- Claude: BIM technical review and evidence check, only after capability verification
- NotebookLM: source-grounded knowledge, only after capability verification
- Gemini: media and Google ecosystem work, only after capability verification
- DeepSeek: low-cost batch processing, only after capability verification
- Perplexity: web discovery, only after capability verification

## Exception States

- `CLAIM_REQUIRES_APPROVAL`
- `COPYRIGHT_RISK`
- `BUSINESS_DM`
- `TECHNICAL_RESULT_UNVERIFIED`
- `PUBLISHING_FAILED`

## Production Path

1. Put this project in a GitHub repository.
2. Connect only the integrations that are officially supported and account-authorized.
3. Update the capability registry in a pull request.
4. Require CI to pass before merge.
5. Run the pipeline from a scheduled worker or GitHub Actions.
6. Publish only after `PUBLISH_GATE` passes with a verified Meta/Instagram capability.
