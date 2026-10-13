# PR Runbook

Use this process before production changes.

## Branch Rules

- one branch per pipeline or integration change
- no direct edits to production config
- capability status changes require proof in the PR description
- CI must pass before merge

## Required PR Evidence

- what changed
- which pipeline states are affected
- which capability was verified, if any
- test result
- rollback plan

## Capability Verification Checklist

Do not mark an integration as verified until the PR includes:

- official documentation link or connected-tool proof
- account permission scope
- rate limit or quota notes
- failure behavior
- sample dry-run result
- owner approval for publishing or external communication

## Meta/Instagram Publishing Gate

Publishing stays blocked unless all are true:

- official Meta/Instagram publishing path supports the BIMNIX account type
- required permissions are granted
- media format is accepted by the API
- publish action is audited in the event bus
- failure returns `PUBLISHING_FAILED`
