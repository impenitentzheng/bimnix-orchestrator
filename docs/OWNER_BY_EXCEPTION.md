# Owner By Exception

The owner should review exceptions in batches, not coordinate every step.

## Weekly Review Target

Keep owner work under 30 minutes per week:

- 10 minutes: approve or reject claims
- 10 minutes: handle business DMs
- 5 minutes: review copyright or credit issues
- 5 minutes: inspect failed publishing or learning-loop summaries

## Owner Queue

The owner queue is any event routed to `owner`.

Run:

```powershell
python -m bimnix_orchestrator.cli owner-queue
```

Important states:

- `CLAIM_REQUIRES_APPROVAL`
- `COPYRIGHT_RISK`
- `BUSINESS_DM`
- `TECHNICAL_RESULT_UNVERIFIED`
- `PUBLISHING_FAILED`

## Decision Format

Owner decisions should be written back as structured payload fields:

- `editorial_decision = approved | rejected | needs_review`
- `owner_note = short reason`
- `approved_claim = exact claim allowed for publishing`
- `publish_allowed = true | false`
