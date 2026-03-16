# F2-B Contracts Real API Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect the contracts list and contract detail UI to the canonical backend API already published in `origin/main`, keeping explicit loading, empty, error, and refresh states.

**Architecture:** Keep the App Router pages as thin composition roots. Extend `entities/contracts` with list and detail mappers, extend `lib/api/contracts.ts` with transport-only readers, keep `/contracts` as the client-side intake plus list screen, and replace the detail placeholder with a dedicated screen under `features/contracts/screens/`. Re-fetch the list after successful uploads instead of fabricating list items locally.

**Tech Stack:** Next.js App Router, React 19, TypeScript, Vitest, React Testing Library, Playwright

---

## Chunk 1: Frontend Data Boundaries

### Task 1: Expand contract entities and transport clients for list and detail

**Files:**
- Modify: `web/src/entities/contracts/model.ts`
- Modify: `web/src/entities/contracts/model.test.ts`
- Modify: `web/src/lib/api/contracts.ts`
- Modify: `web/src/lib/api/contracts.test.ts`

- [ ] **Step 1: Write the failing entity-mapping tests**

Add tests in `web/src/entities/contracts/model.test.ts` for:
- mapping list payload items with `signature_date`, `term_months`, `latest_analysis_status`, `latest_contract_risk_score`, and `latest_version_source`
- mapping detail payload with `contract`, `latest_version`, and `latest_analysis`
- preserving `null` for `latest_version` and `latest_analysis`

```ts
it("maps contract list payloads into UI-facing summaries", () => {
  const result = mapContractListResponse({
    items: [
      {
        id: "ctr-1",
        title: "Loja Centro",
        external_reference: "LOC-001",
        status: "uploaded",
        signature_date: null,
        start_date: null,
        end_date: null,
        term_months: 36,
        latest_analysis_status: "completed",
        latest_contract_risk_score: 80,
        latest_version_source: "third_party_draft",
      },
    ],
  });

  expect(result.items[0].externalReference).toBe("LOC-001");
  expect(result.items[0].latestRiskScore).toBe(80);
});
```

```ts
it("maps contract detail payloads and preserves null derived sections", () => {
  const result = mapContractDetailResponse({
    contract: {
      id: "ctr-1",
      title: "Loja Centro",
      external_reference: "LOC-001",
      status: "uploaded",
      signature_date: null,
      start_date: null,
      end_date: null,
      term_months: 36,
      parties: null,
      financial_terms: null,
    },
    latest_version: null,
    latest_analysis: null,
  });

  expect(result.contract.externalReference).toBe("LOC-001");
  expect(result.latestVersion).toBeNull();
  expect(result.latestAnalysis).toBeNull();
});
```

- [ ] **Step 2: Run the entity tests to verify they fail**

Run: `cd web && npm run test -- src/entities/contracts/model.test.ts`
Expected: FAIL because the list/detail types and mappers do not exist yet.

- [ ] **Step 3: Implement the entity mappings**

In `web/src/entities/contracts/model.ts`, add:
- `ContractListItemSummary`
- `ContractListResponsePayload`
- `ContractDetail`
- `ContractDetailResponsePayload`
- `mapContractListResponse`
- `mapContractDetailResponse`

Use camelCase UI-facing fields such as:
- `externalReference`
- `signatureDate`
- `latestAnalysisStatus`
- `latestRiskScore`
- `latestVersionSource`

Keep upload types and upload mapping intact.

- [ ] **Step 4: Run the entity tests to verify they pass**

Run: `cd web && npm run test -- src/entities/contracts/model.test.ts`
Expected: PASS.

- [ ] **Step 5: Write the failing transport tests**

Add tests in `web/src/lib/api/contracts.test.ts` for:
- `listContracts` returning mapped list summaries
- `getContractDetail` returning mapped detail data
- generic error fallback for list/detail when response body is unusable

```ts
it("maps list contracts payloads from the API", async () => {
  vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
  const fetchImpl: typeof fetch = async () =>
    new Response(
      JSON.stringify({
        items: [
          {
            id: "ctr-1",
            title: "Loja Centro",
            external_reference: "LOC-001",
            status: "uploaded",
            signature_date: null,
            start_date: null,
            end_date: null,
            term_months: 36,
            latest_analysis_status: "completed",
            latest_contract_risk_score: 80,
            latest_version_source: "third_party_draft",
          },
        ],
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );

  const result = await listContracts(fetchImpl);
  expect(result.items[0].latestRiskScore).toBe(80);
});
```

- [ ] **Step 6: Run the transport tests to verify they fail**

Run: `cd web && npm run test -- src/lib/api/contracts.test.ts`
Expected: FAIL because `listContracts` and `getContractDetail` do not exist yet.

- [ ] **Step 7: Implement the transport readers**

In `web/src/lib/api/contracts.ts`:
- add a reusable helper for JSON error detail extraction
- add `listContracts(fetchImpl = fetch)`
- add `getContractDetail(contractId, fetchImpl = fetch)`
- call:
  - `GET ${NEXT_PUBLIC_API_URL}/api/contracts`
  - `GET ${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}`
- map responses through the new `entities/contracts` mappers

- [ ] **Step 8: Run the transport tests to verify they pass**

Run: `cd web && npm run test -- src/lib/api/contracts.test.ts`
Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add web/src/entities/contracts/model.ts web/src/entities/contracts/model.test.ts web/src/lib/api/contracts.ts web/src/lib/api/contracts.test.ts
git commit -m "feat: add contracts list and detail api clients"
```

## Chunk 2: Contracts List Screen

### Task 2: Add the real contracts list to `/contracts`

**Files:**
- Create: `web/src/features/contracts/components/contracts-list-panel.tsx`
- Modify: `web/src/features/contracts/screens/contracts-screen.tsx`
- Modify: `web/src/features/contracts/screens/contracts-screen.test.tsx`

- [ ] **Step 1: Write the failing screen tests for the list states**

Extend `web/src/features/contracts/screens/contracts-screen.test.tsx` with tests for:
- loading list state on initial mount
- empty list copy when no persisted contracts exist
- error state for failed list fetch
- refresh action re-fetching the list
- successful upload triggering a list re-fetch
- clicking a list item navigates to `/contracts/[contractId]`

Use dependency injection on `ContractsScreen` so tests can pass:
- `loadContracts`
- `refreshContracts`
- `navigateToContract`

```tsx
it("shows persisted contracts after loading the list", async () => {
  const loadContracts = vi.fn().mockResolvedValue({
    items: [
      {
        id: "ctr-1",
        title: "Loja Centro",
        externalReference: "LOC-001",
        status: "uploaded",
        signatureDate: null,
        startDate: null,
        endDate: null,
        termMonths: 36,
        latestAnalysisStatus: "completed",
        latestRiskScore: 80,
        latestVersionSource: "third_party_draft",
      },
    ],
  });

  render(<ContractsScreen loadContracts={loadContracts} submitContract={vi.fn()} />);

  expect(await screen.findByText("Loja Centro")).toBeInTheDocument();
  expect(screen.getByText("LOC-001")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the contracts screen tests to verify they fail**

Run: `cd web && npm run test -- src/features/contracts/screens/contracts-screen.test.tsx`
Expected: FAIL because the list panel, loaders, refresh behavior, and navigation hooks do not exist yet.

- [ ] **Step 3: Implement the list panel and screen wiring**

Create `web/src/features/contracts/components/contracts-list-panel.tsx` with:
- section header
- refresh button
- list items
- empty state copy
- error copy

Update `web/src/features/contracts/screens/contracts-screen.tsx` so it:
- loads contracts on mount with `listContracts`
- shows explicit loading/empty/error states for the list
- re-fetches the list after successful upload
- passes click events through a navigation callback
- keeps the existing upload triage behavior intact

Do not replace the upload result with a fake persisted list item.

- [ ] **Step 4: Run the contracts screen tests to verify they pass**

Run: `cd web && npm run test -- src/features/contracts/screens/contracts-screen.test.tsx`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/features/contracts/components/contracts-list-panel.tsx web/src/features/contracts/screens/contracts-screen.tsx web/src/features/contracts/screens/contracts-screen.test.tsx
git commit -m "feat: connect contracts list to real api"
```

## Chunk 3: Contract Detail Route

### Task 3: Replace the contract detail placeholder with a real detail screen

**Files:**
- Create: `web/src/features/contracts/screens/contract-detail-screen.tsx`
- Create: `web/src/features/contracts/screens/contract-detail-screen.test.tsx`
- Create: `web/src/features/contracts/screens/contract-detail-screen.module.css`
- Modify: `web/src/app/(app)/contracts/[contractId]/page.tsx`

- [ ] **Step 1: Write the failing detail screen tests**

Add tests in `web/src/features/contracts/screens/contract-detail-screen.test.tsx` for:
- full detail payload rendering
- partial state when `latest_analysis` is `null`
- partial state when `latest_version` is `null`
- `404` or transport error state
- refresh action for the detail

```tsx
it("renders the latest analysis findings when available", async () => {
  const loadContractDetail = vi.fn().mockResolvedValue({
    contract: {
      id: "ctr-1",
      title: "Loja Centro",
      externalReference: "LOC-001",
      status: "uploaded",
      signatureDate: null,
      startDate: null,
      endDate: null,
      termMonths: 36,
      parties: { tenant: "Loja Centro" },
      financialTerms: { monthlyRent: 12000 },
    },
    latestVersion: {
      contractVersionId: "ver-1",
      source: "third_party_draft",
      originalFilename: "contract.pdf",
      usedOcr: false,
      text: "Prazo de vigencia 36 meses",
    },
    latestAnalysis: {
      analysisId: "ana-1",
      analysisStatus: "completed",
      policyVersion: "v1",
      contractRiskScore: 80,
      findings: [
        {
          id: "finding-1",
          clauseName: "Prazo de vigencia",
          status: "critical",
          severity: "critical",
          currentSummary: "Prazo atual de 36 meses.",
          policyRule: "Prazo minimo exigido: 60 meses.",
          riskExplanation: "Prazo abaixo do minimo permitido pela politica.",
          suggestedAdjustmentDirection: "Solicitar prazo minimo de 60 meses.",
          metadata: {},
        },
      ],
    },
  });

  render(<ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />);

  expect(await screen.findByText("Loja Centro")).toBeInTheDocument();
  expect(screen.getByText("Prazo de vigencia")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the detail screen tests to verify they fail**

Run: `cd web && npm run test -- src/features/contracts/screens/contract-detail-screen.test.tsx`
Expected: FAIL because the detail screen does not exist yet.

- [ ] **Step 3: Implement the detail screen and route composition**

Create `web/src/features/contracts/screens/contract-detail-screen.tsx` as a client component that:
- receives `contractId`
- fetches detail on mount through `getContractDetail`
- renders `PageHeader` + `SurfaceCard`
- shows explicit partial states for missing version or analysis
- exposes a refresh action

Update `web/src/app/(app)/contracts/[contractId]/page.tsx` so it only resolves `params` and renders `ContractDetailScreen`.

- [ ] **Step 4: Run the detail screen tests to verify they pass**

Run: `cd web && npm run test -- src/features/contracts/screens/contract-detail-screen.test.tsx`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/features/contracts/screens/contract-detail-screen.tsx web/src/features/contracts/screens/contract-detail-screen.test.tsx web/src/features/contracts/screens/contract-detail-screen.module.css web/src/app/(app)/contracts/[contractId]/page.tsx
git commit -m "feat: connect contract detail to real api"
```

## Chunk 4: End-to-End Verification and Task Closeout

### Task 4: Add route-level E2E coverage and close the squad artifacts

**Files:**
- Create: `web/tests/e2e/contracts-list-detail.spec.ts`
- Create: `docs/squad/artifacts/2026-03-16-f2-b-contracts-real-api.md`
- Modify: `.codex-memory/current-state.md`
- Modify: `.codex-memory/session-log.md`

- [ ] **Step 1: Write the failing E2E spec**

Add `web/tests/e2e/contracts-list-detail.spec.ts` for:
- list loads persisted contracts from the backend
- operator navigates into a real detail route
- detail renders persisted findings when present

```ts
test("operator opens a persisted contract from the real list", async ({ page }) => {
  await page.goto("/contracts");

  await expect(page.getByText("Loja Centro")).toBeVisible();
  await page.getByRole("link", { name: /Loja Centro/i }).click();

  await expect(page.getByRole("heading", { name: "Loja Centro" })).toBeVisible();
  await expect(page.getByText("Prazo de vigencia")).toBeVisible();
});
```

- [ ] **Step 2: Run the E2E spec to verify it fails**

Run: `cd web && npx playwright test tests/e2e/contracts-list-detail.spec.ts`
Expected: FAIL because the list/detail real flow is not wired yet.

- [ ] **Step 3: Make the E2E spec pass and run the focused verification**

Run: `cd web && npm run test -- src/entities/contracts/model.test.ts src/lib/api/contracts.test.ts src/features/contracts/screens/contracts-screen.test.tsx src/features/contracts/screens/contract-detail-screen.test.tsx`
Run: `cd web && npx playwright test tests/e2e/contracts-list-detail.spec.ts`
Expected: PASS.

- [ ] **Step 4: Record the squad artifact and memory updates**

Create `docs/squad/artifacts/2026-03-16-f2-b-contracts-real-api.md` with:
- task brief
- implementation handoff
- frontend QA review
- documentation update note

Update:
- `.codex-memory/current-state.md`
- `.codex-memory/session-log.md`

Record:
- that `F2-B` now consumes the real list and detail APIs
- actual verification commands and results
- residual risks marked `a confirmar`
- next project step after `F2-B`

- [ ] **Step 5: Commit**

```bash
git add web/tests/e2e/contracts-list-detail.spec.ts docs/squad/artifacts/2026-03-16-f2-b-contracts-real-api.md .codex-memory/current-state.md .codex-memory/session-log.md
git commit -m "docs: close out F2-B contracts real api"
```
