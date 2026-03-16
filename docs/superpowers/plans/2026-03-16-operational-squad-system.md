# Operational Squad System Implementation Plan

**Goal:** Implement the approved repository-native squad system so future work is classified, routed, reviewed, and documented through explicit operational rules instead of ad-hoc role usage.

**Architecture:** Keep the squad implementation lightweight and repository-native. The system lives in `docs/squad/` plus integration rules in `AGENTS.md`, while local memory stays aligned through `./.codex-memory`.

## Task 1: Create the repository-native squad structure

**Files:**
- Create: `docs/squad/README.md`
- Create: `docs/squad/routing-matrix.md`
- Create: `docs/squad/blocking-rules.md`
- Create: `docs/squad/agents/implementation-manager.md`
- Create: `docs/squad/agents/tech-lead.md`
- Create: `docs/squad/agents/backend-engineer.md`
- Create: `docs/squad/agents/frontend-engineer.md`
- Create: `docs/squad/agents/qa-backend.md`
- Create: `docs/squad/agents/qa-frontend.md`
- Create: `docs/squad/agents/documentation-engineer.md`
- Create: `docs/squad/templates/task-brief.md`
- Create: `docs/squad/templates/implementation-handoff.md`
- Create: `docs/squad/templates/architecture-review.md`
- Create: `docs/squad/templates/qa-review.md`
- Create: `docs/squad/templates/documentation-update.md`

- [ ] **Step 1: Create the squad overview and routing docs**

Write the system overview, task entry flow, routing model, task classes, and required artifacts in `docs/squad/README.md`, `routing-matrix.md`, and `blocking-rules.md`.

- [ ] **Step 2: Create one agent file per role**

Each role file must define:
- mission
- ownership
- non-ownership boundaries
- triggers
- inputs
- outputs
- checklist

- [ ] **Step 3: Create the reusable templates**

Add concrete markdown templates for task briefs, implementation handoffs, architecture review, QA review, and documentation update notes.

- [ ] **Step 4: Verify the structure exists**

Run: `rg --files docs/squad`
Expected: all squad docs, agent files, and templates appear in the file list.

## Task 2: Integrate the squad system into the project operating rules

**Files:**
- Modify: `AGENTS.md`
- Modify: `./.codex-memory/teams.md`

- [ ] **Step 1: Update `AGENTS.md`**

Add a squad workflow section that requires:
- task classification before relevant work
- routing through `docs/squad/routing-matrix.md`
- evidence-based blocking through `docs/squad/blocking-rules.md`
- documentation and memory updates before task closure

- [ ] **Step 2: Upgrade `teams.md` from advisory list to official squad map**

Reflect the same roles, ownership model, and activation logic used in `docs/squad/`.

- [ ] **Step 3: Verify `AGENTS.md` and `teams.md` align**

Run:
- `rg -n "implementation-manager|tech-lead|backend-engineer|frontend-engineer|qa-backend|qa-frontend|documentation-engineer" AGENTS.md .codex-memory/teams.md docs/squad`
Expected: all official roles appear consistently across the squad system and local memory.

## Task 3: Verify consistency, document rollout state, and publish

**Files:**
- Modify: `./.codex-memory/current-state.md`
- Modify: `./.codex-memory/session-log.md`

- [ ] **Step 1: Run structural consistency checks**

Run:
- `rg --files docs/squad`
- `rg -n "docs/squad|routing-matrix|blocking-rules" AGENTS.md`
- `rg -n "implementation-manager|tech-lead|backend-engineer|frontend-engineer|qa-backend|qa-frontend|documentation-engineer" .codex-memory/teams.md docs/squad`
Expected: the squad structure exists and references are internally consistent.

- [ ] **Step 2: Update memory with rollout status**

Record that the operational squad system is now implemented in the repository and point to the new primary files.

- [ ] **Step 3: Commit the implementation**

```bash
git add docs/squad AGENTS.md .codex-memory/teams.md .codex-memory/current-state.md .codex-memory/session-log.md docs/superpowers/plans/2026-03-16-operational-squad-system.md
git commit -m "docs: implement operational squad system"
```
