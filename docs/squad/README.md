# Operational Squad System

This repository uses an operational squad model to classify work, route it through the right specialists, and close tasks with explicit evidence instead of ad-hoc role usage.

## Objective
- improve delivery quality without forcing unnecessary ceremony
- keep ownership explicit
- scale review depth by task impact
- make documentation and memory updates part of normal delivery

## When To Use The Squad
- any change that affects `backend/`, `web/`, setup, API contracts, architecture, or operator-facing behavior
- any task that needs verification beyond a single local edit
- any task that could create ambiguity about ownership, review, or readiness

Tiny local-only chores may use the minimum route, but they still start with classification.

## How To Run The Squad
1. Start with `implementation-manager`.
2. Fill a task brief from [`templates/task-brief.md`](./templates/task-brief.md).
3. Route the task using [`routing-matrix.md`](./routing-matrix.md).
4. If the matrix requires architecture review, run `tech-lead` before implementation.
5. Run the assigned engineer path.
6. Produce an implementation handoff from [`templates/implementation-handoff.md`](./templates/implementation-handoff.md).
7. Run the matching QA path.
8. Run `documentation-engineer` whenever behavior, setup, API, UX flow, or operating guidance changed.
9. Close the task only after blockers are cleared and required artifacts exist.

## Task Classes

### Low-Risk Single-Area Task
- examples: isolated backend bug fix, isolated frontend copy-state fix, targeted test addition
- minimum route: `implementation-manager` -> `backend-engineer` or `frontend-engineer` -> matching QA
- add `documentation-engineer` if docs or memory must change

### Medium-Risk Feature Task
- examples: new analysis rule, new screen flow, API extension, non-trivial refactor in one surface
- minimum route: `implementation-manager` -> `tech-lead` if boundaries or contracts move -> `backend-engineer` and or `frontend-engineer` -> matching QA -> `documentation-engineer`

### High-Risk Cross-Cutting Task
- examples: backend plus frontend workflow change, persistence change, deploy-impacting refactor, integration change
- minimum route: `implementation-manager` -> `tech-lead` -> relevant engineer(s) -> relevant QA -> `documentation-engineer`

## Ownership Model
- scope and routing: `implementation-manager`
- architecture and deploy readiness: `tech-lead`
- backend implementation: `backend-engineer`
- frontend implementation: `frontend-engineer`
- backend verification: `qa-backend`
- frontend verification: `qa-frontend`
- documentation and memory coherence: `documentation-engineer`

No decision area has shared ownership. If a conflict appears:
1. `implementation-manager` resolves route and workflow conflicts.
2. `tech-lead` resolves architecture and boundary conflicts.
3. matching QA resolves readiness conflicts for the reviewed area.

## Required Artifacts
- task brief
- implementation handoff
- architecture review when required by route
- QA review for each touched implementation area
- documentation update note when docs, setup, API, UX flow, or memory changed

## Completion Rule
A task is not complete until:
- routing was explicit
- required roles ran
- verification evidence exists
- all objective blockers are resolved
- documentation and memory updates were handled or marked `a confirmar`

## File Map
- [`routing-matrix.md`](./routing-matrix.md)
- [`blocking-rules.md`](./blocking-rules.md)
- [`agents/`](./agents/)
- [`templates/`](./templates/)
