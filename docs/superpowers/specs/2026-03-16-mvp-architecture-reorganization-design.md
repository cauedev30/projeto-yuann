# MVP Architecture Reorganization Design

## Objective
- Reorganize `Projeto_yuann` into a more professional MVP architecture that is easier to evolve, easier to review, and clearer for new engineers without rewriting the product or changing its public behavior.

## Current Context
- The repository is a monorepo with `backend/` for the FastAPI API and services, `web/` for the Next.js operator app, and `docs/` for plans and design documents.
- The product scope is already defined: contract intake, policy analysis, signed-contract archive, critical event monitoring, and operator notifications.
- The current implementation works at MVP level, but some architectural boundaries are still blurred:
  - `backend/app/main.py` still combines app composition with infrastructure wiring.
  - backend business flow is split across `api/routes/`, `services/`, and `tasks/` without a clear application layer.
  - frontend pages still mix composition, screen state, and data wiring.
  - some frontend paths still expose fallback or demo-like data instead of clearly separated fixtures and real integration boundaries.
  - runtime and documentation are not fully aligned on the expected architecture of the MVP.

## Design Goals
- Keep the project as a simple monorepo.
- Preserve current product behavior and routes while improving structure.
- Establish explicit boundaries between product logic, application orchestration, and infrastructure.
- Reduce ambiguity between real integration paths and local/demo/test fixtures.
- Keep the architecture appropriate for an MVP, not an enterprise framework exercise.

## Non-Goals
- Rewrite the app from scratch.
- Introduce full clean architecture or deep DDD ceremony across every module.
- Change the functional scope of the MVP.
- Replace the current stack.

## Architecture Direction

### Monorepo Shape
- Keep:
  - `backend/` for API, domain logic, persistence, and background processing
  - `web/` for the operator application
  - `docs/` for design, plans, and operating documentation
- Improve internal organization so each side has clearer boundaries and fewer mixed responsibilities.

## Backend Target Architecture

### Backend Layering
- `app/main.py`
  - responsibility: application composition root only
  - includes: FastAPI app creation, middleware setup, route registration, startup wiring, and app-state dependency wiring
  - excludes: business flow logic, extraction logic, analysis rules, direct persistence rules

- `app/api/`
  - responsibility: HTTP boundary
  - includes: routes, FastAPI dependencies, request/response schemas, HTTP error mapping
  - excludes: orchestration logic that spans storage, OCR, database updates, and domain decisions

- `app/application/`
  - responsibility: use-case orchestration for MVP workflows
  - includes:
    - contract upload workflow
    - ingestion workflow
    - policy analysis workflow
    - signed-contract archive workflow
    - alert generation workflow
  - role: coordinate domain logic plus infrastructure services without turning routes into orchestrators

- `app/domain/`
  - responsibility: pure or mostly pure business logic
  - includes:
    - contract analysis rules
    - deterministic policy evaluation
    - metadata extraction interpretation
    - event scheduling rules
    - notification eligibility logic
    - core enums and business-level value interpretation when appropriate
  - role: remain understandable and testable without HTTP or framework context

- `app/infrastructure/`
  - responsibility: concrete adapters and wiring details
  - includes:
    - storage services
    - OCR clients
    - LLM client adapters
    - notification delivery adapters
    - persistence wiring helpers that are implementation-specific
  - role: keep framework- and vendor-specific details away from domain logic

- `app/db/`
  - responsibility: persistence model implementation
  - includes: SQLAlchemy models, metadata base, session factory helpers
  - role: stay as the ORM/persistence layer, but no longer act as the center of use-case orchestration

### Backend Flow
- Desired request flow:
  1. `api` receives request and validates the transport contract.
  2. `application` executes the use case.
  3. `domain` evaluates business rules.
  4. `infrastructure` performs external or implementation-specific work.
  5. `api` translates the result back to HTTP.

### Backend Reorganization Targets
- Extract composition and dependency wiring from `main.py` into dedicated factory/bootstrap helpers if needed.
- Move orchestration currently embedded in routes and tasks into explicit `application/` use-case modules.
- Move business-rule-heavy helpers from `services/` into `domain/` when they do not need framework or IO details.
- Keep backward compatibility for existing routes and tests while reshaping internals.

## Frontend Target Architecture

### Frontend Layering
- `src/app/`
  - responsibility: routing, layout, page entrypoints, screen composition roots
  - excludes: reusable business logic and transport-mapping details

- `src/features/`
  - responsibility: user-facing operator workflows grouped by functional context
  - includes:
    - contracts
    - analysis
    - dashboard
    - notifications
  - role: hold screen states, interaction logic, and feature-level UI composition

- `src/entities/`
  - responsibility: central product entities and their frontend-facing types/mappers
  - includes:
    - contract
    - finding
    - event
    - notification
  - role: prevent API payload shapes from leaking directly into all UI components

- `src/lib/` or `src/shared/`
  - responsibility: cross-cutting frontend utilities
  - includes:
    - env loading
    - generic helpers
    - formatting
    - shared fetch utilities if needed

- `src/lib/api/` or `src/infrastructure/api/`
  - responsibility: transport clients only
  - includes: HTTP calls, response mapping, transport-specific serialization
  - excludes: fallback snapshots pretending to be real data sources

### Frontend Flow
- Desired page flow:
  1. `app` entrypoint assembles the page.
  2. `features` manage screen behavior, state transitions, and UI composition.
  3. `entities` define stable business-facing shapes for UI use.
  4. `api` or infrastructure layer maps network payloads to those shapes.

### Frontend Reorganization Targets
- Convert current pages into composition roots rather than mixed state-and-transport modules.
- Move business-facing types out of raw API modules when those types are reused by UI components.
- Replace dashboard fallback snapshots in the main runtime path with explicit real integration boundaries and honest loading/empty/error states.
- Keep test fixtures and demo data available, but relocate them into explicit fixture/test helpers.

## Migration Strategy

### Principle
- Migrate incrementally with behavior preservation.

### Sequence
1. Establish target folders and move code without changing external behavior.
2. Extract backend composition and use-case orchestration from routes and `main.py`.
3. Separate backend business rules from IO-heavy service modules.
4. Introduce frontend entity boundaries and clearer API mapping.
5. Remove fake runtime data paths from production-facing frontend flows.
6. Update README, docs, and project memory to reflect the new architecture.

### Compatibility Rules
- Existing public API endpoints remain stable during the refactor.
- Existing page routes remain stable during the refactor.
- Existing tests should keep passing except where updated to reflect cleaner boundaries.
- Any necessary behavior change must be explicit and justified, not accidental.

## Repository-Level Organization Outcomes
- A new engineer should be able to identify:
  - where HTTP starts and ends
  - where use-case orchestration lives
  - where business rules live
  - where concrete adapters live
  - where UI routing ends and feature logic begins
- The repository should communicate "serious MVP" rather than "working prototype with mixed layers."

## Error Handling and Risks
- Risk: over-refactoring into architecture for architecture's sake.
  - mitigation: preserve MVP simplicity and move only what clarifies boundaries.
- Risk: introducing regressions while moving orchestration.
  - mitigation: keep TDD and existing verification suites active during each migration step.
- Risk: creating duplicate abstractions during transition.
  - mitigation: migrate by responsibility, then remove superseded paths quickly.
- Risk: frontend losing practical velocity because of too many structural layers.
  - mitigation: keep the frontend layered, but shallow and feature-oriented.

## Verification Strategy
- Backend verification:
  - existing API, service, DB, and task tests remain green
  - new tests protect application-layer orchestration where extracted
- Frontend verification:
  - component tests remain green
  - E2E tests still cover operator-critical flows
  - fallback/demo data is no longer the default runtime source for production-facing pages
- Structural verification:
  - `main.py` is reduced to composition concerns
  - pages act as composition roots
  - domain logic becomes easier to locate and reason about
  - README and docs describe the architecture that the code actually follows

## Success Criteria
- The backend has clear separation between HTTP, application orchestration, business rules, and infrastructure.
- The frontend has clear separation between routes, features, entities, and transport clients.
- The MVP remains easy to run locally.
- The repository becomes easier to navigate and easier to extend.
- The architecture looks intentional and professional without exceeding MVP needs.

## Rollout Scope
- Phase 1 covers architectural reorganization and documentation alignment.
- Future phases may continue improving runtime infrastructure alignment, but this design does not require a full platform rewrite.
