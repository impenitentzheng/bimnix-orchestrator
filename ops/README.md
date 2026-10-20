# BIMNIX CEO Resource Dashboard R05

Purpose: a read-only control-plane surface for resource, task, quota, heartbeat, blocker, and event state.

## Privacy boundary

This repository is public. Do **not** commit client names, project codes, credentials, internal NPE data, private task descriptions, or live device identifiers here.

Live/private state must come from a private/local endpoint or a user-selected JSON file at runtime. `state.example.json` is synthetic only.

## State contract

Top-level fields:
- `generated_at`: ISO-8601 timestamp.
- `resources[]`: agents/devices/services with `id`, `kind`, `status`, `heartbeat_at`, optional `quota`.
- `tasks[]`: work items with `id`, `title`, `priority`, `status`, `owner`, optional `blocker`, `deadline`, `resume_at`.
- `events[]`: append-only operational events with `at`, `type`, `subject`, `message`.

Status values are deliberately small: `ACTIVE`, `BLOCKED`, `HOLD`, `DONE`, `UNKNOWN`.

## Runtime inputs

`dashboard.html` supports two non-persistent ways to provide state:
1. choose a JSON file from the local machine; or
2. open with `?endpoint=<https-url>` and press **Fetch endpoint**.

The dashboard never treats missing data as healthy. Missing/invalid fields render as `UNKNOWN`.

## Verification

R05 has structural validation plus browser E2E coverage. The browser test opens the actual dashboard in headless Chromium and verifies:
- the synthetic repository example renders through the real browser code path;
- a private/local JSON file can be loaded without committing its contents to this public repository;
- KPI/task/event values update from the selected local state;
- plaintext HTTP endpoint mode is rejected and HTTPS remains mandatory.

This verifies the runtime loading boundary, not a production private endpoint deployment. Live endpoint hosting/authentication remains a separate private infrastructure decision.

## Architecture

Resource Registry -> Heartbeat -> Task Registry -> Event Log -> Dashboard.

Alerts and auto-routing are intentionally outside R05. R05 establishes an inspectable shared-state contract and a verified local/private-state viewing path first.