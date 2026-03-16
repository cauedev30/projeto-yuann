# Blocking Rules

Blocks are conditional, evidence-based, and limited to objective failures. Subjective preferences do not block delivery.

## Tech Lead Blocks
`tech-lead` may block only for:
- architecture violations against the approved MVP structure
- unsafe or incompatible API contract changes
- persistence or integration changes that break system boundaries
- deploy-readiness risk with concrete impact
- missing architectural decision recording when the task creates a durable new rule

## Backend QA Blocks
`qa-backend` may block only for:
- failing backend tests or missing backend verification evidence
- reproducible backend regressions
- objective mismatch between backend implementation and requirements
- critical reliability or performance risk in touched backend scope

## Frontend QA Blocks
`qa-frontend` may block only for:
- failing frontend tests or missing frontend verification evidence
- reproducible frontend regressions
- missing required loading, empty, error, or accessibility-critical states in changed flows
- objective mismatch between shipped UI behavior and requirements
- critical usability or performance risk in touched frontend scope

## Documentation Blocks
`documentation-engineer` may block only for:
- missing required setup, API, UX-flow, or operating documentation
- missing mandatory memory updates on task closure
- documentation that contradicts shipped behavior

## Non-Blocking Feedback
The following never block on their own:
- style preference
- optional refactor
- nice-to-have UX polish
- speculative optimization without evidence

## Required Block Format
Every block must include:
- role
- violated rule
- concrete evidence
- minimum fix required to unblock

## Escalation Order
1. `implementation-manager` resolves route and workflow disputes.
2. `tech-lead` resolves architecture disputes.
3. matching QA resolves delivery-readiness disputes for the reviewed area.
