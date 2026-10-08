# BIMNIX 0.19 — Public Demo Launch Switch

Status: PREPARED / RELEASE-LOCKED

Do not open the public download until the exact 0.19.0 release artifact is final.

## Release prerequisites

- [ ] `bimnix-core` exact release commit is locked
- [ ] package/app version = `0.19.0`
- [ ] exact release artifact SHA-256 recorded
- [ ] `npm test` passes on exact release commit
- [ ] full E2E/regression passes on exact release build
- [ ] Windows review passes
- [ ] independent coordinate oracle passes
- [ ] final bSI files are regenerated from exact release build
- [ ] final bSI results match approved 0.19 gate
- [ ] release notes include known coordinate/georeferencing limitations

## Website launch switch

1. Upload/host the exact `0.19.0` public-demo artifact.
2. Update download gateway to the exact artifact; never point at an older candidate.
3. Change landing CTA from locked state to the gated tester form/download flow.
4. Update Demo Intake metadata/default app version from `0.17.0` to `0.19.0` where still present.
5. Update feedback page/default app version to `0.19.0`.
6. Keep name/email/role + consent before identified download flow.
7. Keep contact permission separate from download consent.
8. Verify `visit → download_intent → tester → download` events with one real test session.
9. Verify feedback page records one `feedback_open` and one `feedback_submit` only (avoid double counting).
10. Verify UTM source/medium/campaign persistence from landing and feedback.
11. Test Chrome + Edge download flow.
12. Only then remove `noindex,nofollow` if public discovery is intended.

## Claim discipline

Allowed wording after gate:
- BIMNIX 0.19 Experimental Demo
- IFC4 export/import within the supported slice
- Coordinate / Georeferencing Foundation
- Case B outputs validated through buildingSMART Validation Service for the tested release samples

Do not claim:
- buildingSMART software certification
- production readiness
- all IFC classes
- automatic CRS inference
- proof that a browser download event means the file was actually opened locally

## Current public-page state

- Download: LOCKED
- Landing analytics: enabled through `demo-intake`
- Privacy page: present
- Release artifact: not attached yet
- Public demo: not launched yet
