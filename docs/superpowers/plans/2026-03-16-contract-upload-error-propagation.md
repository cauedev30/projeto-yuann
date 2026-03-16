# Contract Upload Error Propagation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the contracts frontend show a clear Portuguese error when the backend rejects an unreadable PDF upload.

**Architecture:** Keep HTTP error parsing and translation inside `web/src/lib/api/contracts.ts`, where transport concerns already live. Let `ContractsScreen` continue rendering thrown `Error.message`, with focused tests at the API client, screen, and E2E layers.

**Tech Stack:** Next.js 15, React 19, TypeScript, Vitest, Testing Library, Playwright

---

## Chunk 1: Transport And Screen Behavior

### Task 1: Map backend upload errors in the transport client

**Files:**
- Modify: `web/src/lib/api/contracts.ts`
- Create: `web/src/lib/api/contracts.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
it("maps unreadable-pdf backend detail into Portuguese copy", async () => {
  await expect(
    uploadContract(input, async () =>
      new Response(JSON.stringify({ detail: "Uploaded file is not a readable PDF" }), {
        status: 422,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  ).rejects.toThrow("O arquivo enviado nao e um PDF legivel.");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm run test -- src/lib/api/contracts.test.ts`
Expected: FAIL because the client still throws the generic upload message.

- [ ] **Step 3: Write minimal implementation**

```typescript
async function extractUploadErrorMessage(response: Response): Promise<string> {
  const payload = (await response.json()) as { detail?: unknown };
  if (payload.detail === "Uploaded file is not a readable PDF") {
    return "O arquivo enviado nao e um PDF legivel.";
  }
  if (typeof payload.detail === "string" && payload.detail.trim()) {
    return payload.detail;
  }
  return "Nao foi possivel enviar o contrato.";
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npm run test -- src/lib/api/contracts.test.ts`
Expected: PASS

### Task 2: Prove the contracts screen renders the mapped message

**Files:**
- Modify: `web/src/features/contracts/screens/contracts-screen.test.tsx`

- [ ] **Step 1: Write the failing test**

```typescript
it("shows the propagated upload error", async () => {
  render(
    <ContractsScreen
      submitContract={vi.fn().mockRejectedValue(new Error("O arquivo enviado nao e um PDF legivel."))}
    />,
  );
  // submit through the form and assert the alert text
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm run test -- src/features/contracts/screens/contracts-screen.test.tsx`
Expected: FAIL until the test drives the real submit flow.

- [ ] **Step 3: Write minimal implementation**

```typescript
// No production change expected if the screen already renders Error.message.
// Adjust only if the test reveals a missing screen behavior.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npm run test -- src/features/contracts/screens/contracts-screen.test.tsx`
Expected: PASS

## Chunk 2: End-To-End Validation

### Task 3: Validate invalid upload with a file from disk

**Files:**
- Create: `web/tests/fixtures/unreadable-upload.pdf`
- Modify: `web/tests/e2e/contract-analysis.spec.ts`

- [ ] **Step 1: Write the failing test**

```typescript
test("operator sees a readable error for an unreadable pdf upload", async ({ page }) => {
  await page.goto("/contracts");
  await page.getByLabel("Titulo do contrato").fill("Loja Centro");
  await page.getByLabel("Referencia externa").fill("LOC-ERR-001");
  await page.getByLabel("Contrato PDF").setInputFiles("tests/fixtures/unreadable-upload.pdf");
  await page.getByRole("button", { name: "Enviar contrato" }).click();

  await expect(page.getByRole("alert")).toContainText("O arquivo enviado nao e um PDF legivel.");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npx playwright test tests/e2e/contract-analysis.spec.ts --grep "unreadable pdf upload"`
Expected: FAIL because the UI still shows the generic upload error.

- [ ] **Step 3: Write minimal implementation**

```typescript
// Reuse the transport-level error translation added in Task 1.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npx playwright test tests/e2e/contract-analysis.spec.ts --grep "unreadable pdf upload"`
Expected: PASS
