# Operational Squad System Design

## Objective
- Create an operational squad system inside the repository so project work is routed through specialized agents that improve delivery quality and speed without adding unnecessary ceremony.

## Context
- `Projeto_yuann` is a LegalTech MVP monorepo with `backend/` for the FastAPI API and services, `web/` for the Next.js operator app, and `./.codex-memory` for persistent operating context.
- The current project already has a lightweight agent map in `./.codex-memory/teams.md`, but it is only advisory and does not define ownership, routing, blocking rules, or handoff artifacts.
- The new system must stay aligned with the MVP goal: keep execution fast, keep responsibilities explicit, and avoid role overlap that creates review noise.

## Design Goals
- Make agent participation useful, not decorative.
- Optimize for MVP delivery speed and objective quality checks.
- Prevent ownership conflicts by giving each decision area one clear owner.
- Scale the process by task impact instead of forcing every role into every task.
- Keep the system repository-native through docs, templates, and operating rules.

## Non-Goals
- Build a runtime orchestration service or external automation platform.
- Change the product architecture of the LegalTech MVP itself.
- Force every task through the full squad when a smaller route is sufficient.

## Operating Principles
- Every relevant task starts with classification.
- Every phase of a task has one owner.
- Routing is automatic by rule, with manual override when a task has unusual risk.
- Blocking is conditional and evidence-based.
- Documentation is part of delivery, not an optional afterthought.
- Memory updates stay mandatory through `AGENTS.md` and `./.codex-memory`.

## Squad Roles

### implementation-manager
- Mission: classify incoming work, define execution route, sequence the handoffs, and ensure the right specialists are engaged.
- Owns: scope framing, task routing, priority interpretation, required artifacts per task.
- Does not own: architecture approval, code implementation approval, or QA sign-off.
- Inputs: user request, changed areas, delivery risk, current memory state, source-of-truth files.
- Outputs: task classification, required agent list, task route, handoff checklist.

### tech-lead
- Mission: preserve MVP architecture quality and deploy readiness.
- Owns: architecture decisions, API contract impact, persistence boundaries, integration boundaries, deploy-readiness concerns.
- Does not own: delivery priority or direct implementation of every task.
- Inputs: task classification, proposed technical change, affected source-of-truth files.
- Outputs: architecture approval, architecture constraints, blocking findings when needed.

### backend-engineer
- Mission: implement backend changes using project stack conventions, clean code, typed contracts, and existing backend patterns.
- Owns: implementation inside `backend/`, backend tests, and backend-facing refactors directly tied to the task.
- Does not own: frontend behavior validation or final QA approval.
- Inputs: routed task, architecture constraints, existing backend source-of-truth files.
- Outputs: backend code changes, tests, backend handoff summary.

### frontend-engineer
- Mission: implement operator-facing flows with strong usability, clear states, and stack-aligned frontend patterns.
- Owns: implementation inside `web/`, frontend tests, and frontend-facing refactors directly tied to the task.
- Does not own: backend behavior validation or final QA approval.
- Inputs: routed task, architecture constraints, existing frontend source-of-truth files.
- Outputs: frontend code changes, tests, frontend handoff summary.

### qa-backend
- Mission: validate backend behavior, architecture adherence, performance-sensitive risks, and backend verification evidence.
- Owns: backend quality gate for touched backend scope.
- Does not own: rewriting scope, reprioritizing the task, or blocking on subjective preferences.
- Inputs: backend diff, backend tests, architecture constraints, backend handoff summary.
- Outputs: backend QA review with pass, recommendation, or objective block.

### qa-frontend
- Mission: validate frontend behavior, usability-critical flows, UI consistency, and frontend verification evidence.
- Owns: frontend quality gate for touched frontend scope.
- Does not own: backend review or subjective design bikeshedding.
- Inputs: frontend diff, frontend tests, UI states, frontend handoff summary.
- Outputs: frontend QA review with pass, recommendation, or objective block.

### documentation-engineer
- Mission: keep technical, operational, and user-facing documentation coherent with the delivered system.
- Owns: documentation completeness for changed behavior, setup, API, operating flow, and memory maintenance guidance.
- Does not own: architectural approval beyond accurate recording.
- Inputs: approved implementation output, QA results, changed files, memory rules from `AGENTS.md`.
- Outputs: documentation updates, memory update checklist, documentation review summary.

## Decision Ownership Model
- Scope and routing: `implementation-manager`
- Architecture and deploy-readiness: `tech-lead`
- Backend implementation: `backend-engineer`
- Frontend implementation: `frontend-engineer`
- Backend verification: `qa-backend`
- Frontend verification: `qa-frontend`
- Documentation and operational coherence: `documentation-engineer`

No decision area has dual ownership. If a conflict appears, resolution follows this order:
1. `implementation-manager` resolves workflow and routing conflicts.
2. `tech-lead` resolves architecture and boundary conflicts.
3. `qa-backend` or `qa-frontend` resolves delivery-readiness conflicts for their reviewed area.

## Routing Model

### Base Rule
- Every relevant task enters through `implementation-manager`.

### Automatic Routing
- Trigger `tech-lead` when a task changes architecture, API contracts, persistence, integrations, deployment behavior, or cross-cutting flows.
- Trigger `backend-engineer` when files under `backend/` or backend contracts are affected.
- Trigger `frontend-engineer` when files under `web/` or operator UX flows are affected.
- Trigger `qa-backend` after backend implementation work.
- Trigger `qa-frontend` after frontend implementation work.
- Trigger `documentation-engineer` when behavior, setup, API, UX flow, or operating guidance changes.

### Manual Override
- `implementation-manager` may add agents for high-risk or cross-functional work even if a simple path would not normally require them.
- Manual override cannot remove mandatory QA for touched implementation areas.

## Task Classes

### Low-Risk Single-Area Task
- Examples: isolated backend bug fix, isolated frontend copy-state correction, targeted test addition.
- Route:
  1. `implementation-manager`
  2. domain engineer
  3. matching QA
  4. `documentation-engineer` if docs or memory must change

### Medium-Risk Feature Task
- Examples: new backend service, new screen flow, API extension, new analysis rule.
- Route:
  1. `implementation-manager`
  2. `tech-lead` if boundaries or contracts change
  3. domain engineer(s)
  4. matching QA
  5. `documentation-engineer`

### High-Risk Cross-Cutting Task
- Examples: backend plus frontend workflow changes, persistence changes, deploy-impacting refactor, integration changes.
- Route:
  1. `implementation-manager`
  2. `tech-lead`
  3. `backend-engineer` and or `frontend-engineer`
  4. `qa-backend` and or `qa-frontend`
  5. `documentation-engineer`

## Blocking Rules

### tech-lead Can Block Only For
- architecture violation against the approved MVP structure
- incompatible or unsafe API contract changes
- persistence or integration changes that break system boundaries
- deploy-readiness risk with objective impact
- missing architectural decision documentation when the change creates a durable new rule

### QA Can Block Only For
- failing tests or missing verification evidence
- reproducible regression
- objective mismatch between implementation and requirements
- critical performance or reliability risk in changed scope
- missing required states, accessibility-critical behavior, or usability-critical flow coverage in changed frontend scope

### documentation-engineer Can Block Only For
- required documentation missing for changed setup, API, or operator flow
- mandatory memory updates omitted when the task is being closed
- documentation that contradicts shipped behavior

### Non-Blocking Feedback
- style preference
- optional refactor
- nice-to-have UX improvements
- speculative optimization without measurable need

Every block must include:
- the blocking role
- the violated rule
- concrete evidence
- the minimum fix required to unblock

## Task Flow
1. Request arrives.
2. `implementation-manager` creates task classification and routing decision.
3. `tech-lead` reviews if routing rules require architectural validation.
4. Assigned engineer implements within scoped area.
5. Engineer produces handoff summary and verification evidence.
6. Matching QA reviews touched scope and either passes, recommends, or blocks.
7. `documentation-engineer` updates documentation and memory-related artifacts when applicable.
8. Task closes only when required approvals and evidence exist.

## Required Artifacts

### implementation-manager Artifact
- task brief with scope, risk level, affected areas, required agents, and expected outputs

### Engineer Artifact
- implementation handoff containing changed files, behavior summary, tests run, and known residual risks

### QA Artifact
- review note containing reviewed scope, evidence checked, result status, and blocking findings if any

### Documentation Artifact
- documentation update note listing updated docs, memory files touched, and remaining `a confirmar` items

## Repository Structure
- `docs/squad/README.md`: squad overview and entry flow
- `docs/squad/routing-matrix.md`: routing rules by task type, risk, and affected areas
- `docs/squad/blocking-rules.md`: objective blocking criteria and escalation rules
- `docs/squad/agents/`: one file per agent with mission, triggers, inputs, outputs, and checklist
- `docs/squad/templates/`: reusable templates for task brief, handoff, architecture review, QA review, and documentation review

## Integration With Existing Project Rules
- `AGENTS.md` must instruct workers to consult the squad system for relevant tasks.
- `./.codex-memory/teams.md` must be upgraded from a loose list of possible agents to the official squad map.
- Memory maintenance rules remain active and are enforced by the documentation path, not replaced by it.
- The squad system must stay compatible with the existing MVP plan and source-of-truth files.

## Error Handling and Failure Modes
- If task classification is ambiguous, `implementation-manager` defaults upward in rigor instead of skipping a needed specialist.
- If two roles disagree, the issue is resolved using the ownership hierarchy instead of parallel debate.
- If a required specialist is unavailable in the current harness, the workflow must record the gap explicitly as `a confirmar` or execute the closest equivalent review path.
- If a task is too small for full routing, the routing matrix still applies, but only the mandatory minimum path is used.

## Verification Strategy
- Verify the squad system by checking that role files, routing rules, blocking rules, and templates are internally consistent.
- Verify that `AGENTS.md` and `./.codex-memory/teams.md` point to the same operational model.
- Verify that the repository contains enough explicit guidance for a future worker to classify and route a task without relying on hidden context.

## Rollout Scope
- Phase 1 introduces the repository-native squad system and project operating rules.
- Future evolution may add helper scripts or CLI support, but that is intentionally out of scope for this design.
