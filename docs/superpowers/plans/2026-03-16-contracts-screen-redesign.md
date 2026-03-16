# Contracts Screen Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesenhar a tela `/contracts` para um fluxo guiado, profissional e responsivo, mantendo compatibilidade com o contrato atual de upload e sem tocar no backend.

**Architecture:** Manter `web/src/app/(app)/contracts/page.tsx` como composition root e concentrar a orquestracao visual em `ContractsScreen`, extraindo blocos de UI com responsabilidades claras para hero, estado da sessao, resumo executivo e detalhes. Usar TDD para proteger estados e hierarquia antes de extrair componentes e aplicar estilo local da feature.

**Tech Stack:** Next.js App Router, React 19, TypeScript, Vitest, Testing Library, CSS Modules

---

## Workflow Notes
- Executar em worktree isolado com `@superpowers:using-git-worktrees` antes de implementar.
- Seguir `@superpowers:test-driven-development` em toda mudanca de comportamento.
- Pedir review ao final do bloco de implementacao com `@superpowers:requesting-code-review` se o harness permitir.
- Antes de declarar conclusao, rodar verificacoes frescas com `@superpowers:verification-before-completion`.
- Nao registrar secrets do Trello em arquivos do repositorio; usar credenciais ja existentes apenas no ambiente de execucao.

## Planned File Structure
- Modify: `web/src/features/contracts/screens/contracts-screen.tsx`
  - continuar como composition root da feature, coordenando `isSubmitting`, `result`, `error` e a montagem dos blocos visuais.
- Modify: `web/src/features/contracts/screens/contracts-screen.test.tsx`
  - proteger os estados `vazio`, `loading`, `erro` e `sucesso`, incluindo a ordem resumo -> detalhes.
- Create: `web/src/features/contracts/screens/contracts-screen.module.css`
  - guardar layout, cards, espacos e regras responsivas da tela.
- Create: `web/src/features/contracts/components/contracts-hero.tsx`
  - renderizar contexto da tela e cabecalho operacional.
- Create: `web/src/features/contracts/components/session-status-card.tsx`
  - comunicar o estado atual da sessao.
- Create: `web/src/features/contracts/components/upload-summary-cards.tsx`
  - exibir resumo executivo apos sucesso.
- Create: `web/src/features/contracts/components/findings-section.tsx`
  - enquadrar findings com titulo e contexto visual.
- Create: `web/src/features/contracts/components/extracted-text-panel.tsx`
  - exibir o texto extraido em painel secundario.
- Modify: `web/src/features/contracts/components/upload-form.tsx`
  - manter contrato atual do formulario, mas refinar estrutura, rotulos e feedbacks de submissao.
- Modify: `web/src/features/contracts/components/upload-form.test.tsx`
  - proteger comportamento do formulario refinado.
- Create: `web/src/features/contracts/components/upload-form.module.css`
  - guardar estilo local do formulario e da area de arquivo.
- Modify: `.codex-memory/current-state.md`
  - registrar o estado verificado apos concluir o card.
- Modify: `.codex-memory/session-log.md`
  - registrar uma entrada curta da sessao.

## Chunk 1: Screen State Model and Layout

### Task 1: Protect the contracts screen states before changing the UI

**Files:**
- Modify: `web/src/features/contracts/screens/contracts-screen.test.tsx`
- Modify: `web/src/features/contracts/screens/contracts-screen.tsx`

- [ ] **Step 1: Write the failing screen tests for the guided flow**

```tsx
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ContractsScreen } from "./contracts-screen";

function buildUploadResult() {
  return {
    contractId: "contract-1",
    contractVersionId: "version-1",
    source: "third_party_draft" as const,
    usedOcr: false,
    text: "Prazo de vigencia 36 meses",
  };
}

describe("ContractsScreen", () => {
  it("shows the guided empty state before any upload", () => {
    render(<ContractsScreen submitContract={vi.fn()} />);

    expect(
      screen.getByText("Envie um contrato para triagem inicial"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Nenhuma triagem foi executada nesta sessao."),
    ).toBeInTheDocument();
  });

  it("shows processing feedback while the upload is pending", async () => {
    const user = userEvent.setup();
    let resolveUpload: ((value: ReturnType<typeof buildUploadResult>) => void) | undefined;
    const submitContract = vi.fn(
      () =>
        new Promise<ReturnType<typeof buildUploadResult>>((resolve) => {
          resolveUpload = resolve;
        }),
    );

    render(<ContractsScreen submitContract={submitContract} />);

    await user.type(screen.getByLabelText("Titulo do contrato"), "Loja Centro");
    await user.type(screen.getByLabelText("Referencia externa"), "LOC-001");
    await user.upload(
      screen.getByLabelText("Contrato PDF"),
      new File(["dummy"], "contract.pdf", { type: "application/pdf" }),
    );
    await user.click(screen.getByRole("button", { name: "Enviar contrato" }));

    expect(screen.getByText("Processando triagem inicial...")).toBeInTheDocument();

    resolveUpload?.(buildUploadResult());
    await waitFor(() =>
      expect(screen.getByText("Triagem inicial concluida")).toBeInTheDocument(),
    );
  });

  it("shows a contextual error and keeps the form available after a failed upload", async () => {
    const user = userEvent.setup();
    const submitContract = vi.fn().mockRejectedValue(new Error("Falha no envio"));

    render(<ContractsScreen submitContract={submitContract} />);

    await user.type(screen.getByLabelText("Titulo do contrato"), "Loja Centro");
    await user.type(screen.getByLabelText("Referencia externa"), "LOC-001");
    await user.upload(
      screen.getByLabelText("Contrato PDF"),
      new File(["dummy"], "contract.pdf", { type: "application/pdf" }),
    );
    await user.click(screen.getByRole("button", { name: "Enviar contrato" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Falha no envio");
    expect(screen.getByRole("button", { name: "Enviar contrato" })).toBeEnabled();
  });

  it("renders the summary before findings and extracted text after success", async () => {
    const user = userEvent.setup();
    const submitContract = vi.fn().mockResolvedValue(buildUploadResult());

    render(<ContractsScreen submitContract={submitContract} />);

    await user.type(screen.getByLabelText("Titulo do contrato"), "Loja Centro");
    await user.type(screen.getByLabelText("Referencia externa"), "LOC-001");
    await user.upload(
      screen.getByLabelText("Contrato PDF"),
      new File(["dummy"], "contract.pdf", { type: "application/pdf" }),
    );
    await user.click(screen.getByRole("button", { name: "Enviar contrato" }));

    const summaryHeading = await screen.findByRole("heading", { name: "Resumo da triagem" });
    const findingsHeading = screen.getByRole("heading", { name: "Findings principais" });
    const extractedTextHeading = screen.getByRole("heading", { name: "Texto extraido" });

    expect(
      summaryHeading.compareDocumentPosition(findingsHeading) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(
      findingsHeading.compareDocumentPosition(extractedTextHeading) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run the targeted screen tests to verify they fail**

Run: `cd web && npm run test -- src/features/contracts/screens/contracts-screen.test.tsx`
Expected: FAIL because the current screen does not expose the guided empty state, processing copy, contextual status card, or the new result sections.

- [ ] **Step 3: Implement the minimal guided state model in `ContractsScreen`**

```tsx
const [isSubmitting, setIsSubmitting] = useState(false);
const [result, setResult] = useState<ContractUploadResult | null>(null);
const [error, setError] = useState<string | null>(null);

const statusState = error
  ? "error"
  : isSubmitting
    ? "loading"
    : result
      ? "success"
      : "empty";
```

Render the following placeholders directly in `ContractsScreen` before extraction:
- hero copy with `Envie um contrato para triagem inicial`
- session status copy for `empty`, `loading`, `error`, `success`
- headings `Resumo da triagem`, `Findings principais`, `Texto extraido`

Keep the existing `UploadForm`, `RiskScoreCard`, `FindingsTable`, and `result.text` wiring alive while adding the new headings and state copy.

- [ ] **Step 4: Run the targeted screen tests to verify they pass**

Run: `cd web && npm run test -- src/features/contracts/screens/contracts-screen.test.tsx`
Expected: PASS with 4 passing tests.

- [ ] **Step 5: Commit the red-green screen-state protection**

```bash
git add web/src/features/contracts/screens/contracts-screen.tsx web/src/features/contracts/screens/contracts-screen.test.tsx
git commit -m "test: protect contracts screen guided states"
```

### Task 2: Refactor the screen into focused visual components and local layout styles

**Files:**
- Create: `web/src/features/contracts/screens/contracts-screen.module.css`
- Create: `web/src/features/contracts/components/contracts-hero.tsx`
- Create: `web/src/features/contracts/components/session-status-card.tsx`
- Create: `web/src/features/contracts/components/upload-summary-cards.tsx`
- Create: `web/src/features/contracts/components/findings-section.tsx`
- Create: `web/src/features/contracts/components/extracted-text-panel.tsx`
- Modify: `web/src/features/contracts/screens/contracts-screen.tsx`
- Test: `web/src/features/contracts/screens/contracts-screen.test.tsx`

- [ ] **Step 1: Refactor the now-green screen into focused components**

Move the placeholder UI from `ContractsScreen` into these components:

```tsx
export function ContractsHero() {
  return (
    <header>
      <p>Governanca contratual</p>
      <h1>Envie um contrato para triagem inicial</h1>
      <p>Suba um PDF para executar a triagem inicial e revisar o resultado da sessao.</p>
    </header>
  );
}
```

```tsx
type SessionStatusCardProps = {
  state: "empty" | "loading" | "error" | "success";
  message?: string;
};
```

```tsx
type UploadSummaryCardsProps = {
  source: ContractSource;
  usedOcr: boolean;
  riskScore: number;
  hasCriticalFinding: boolean;
};
```

Keep `ContractsScreen` responsible only for:
- local state
- `handleSubmit`
- deriving findings and score
- passing props into extracted blocks

- [ ] **Step 2: Add the screen-level CSS module for layout and responsiveness**

Use `contracts-screen.module.css` to define:
- page shell and surface blocks
- desktop two-column layout for upload + session status
- stacked mobile layout
- summary cards row that collapses on narrow screens
- result panels with consistent spacing and hierarchy

Do not introduce global CSS or touch `src/app/layout.tsx`.

- [ ] **Step 3: Re-run the protected screen tests after the refactor**

Run: `cd web && npm run test -- src/features/contracts/screens/contracts-screen.test.tsx`
Expected: PASS with the same 4 tests still green after the component extraction.

- [ ] **Step 4: Build the web app to catch CSS-module or import mistakes early**

Run: `cd web && npm run build`
Expected: PASS with a clean Next.js production build.

- [ ] **Step 5: Commit the extracted screen composition**

```bash
git add web/src/features/contracts/screens/contracts-screen.tsx web/src/features/contracts/screens/contracts-screen.test.tsx web/src/features/contracts/screens/contracts-screen.module.css web/src/features/contracts/components/contracts-hero.tsx web/src/features/contracts/components/session-status-card.tsx web/src/features/contracts/components/upload-summary-cards.tsx web/src/features/contracts/components/findings-section.tsx web/src/features/contracts/components/extracted-text-panel.tsx
git commit -m "feat: compose contracts screen with guided layout"
```

## Chunk 2: Upload Panel Polish and Completion

### Task 3: Refine the upload form presentation and busy-state behavior

**Files:**
- Create: `web/src/features/contracts/components/upload-form.module.css`
- Modify: `web/src/features/contracts/components/upload-form.tsx`
- Modify: `web/src/features/contracts/components/upload-form.test.tsx`
- Modify: `web/src/features/contracts/screens/contracts-screen.tsx`
- Modify: `web/src/features/contracts/screens/contracts-screen.module.css`

- [ ] **Step 1: Write the failing upload-form tests for the refined UX**

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { UploadForm } from "./upload-form";

describe("UploadForm", () => {
  it("keeps the submit button disabled until a PDF is selected", () => {
    render(<UploadForm onSubmit={vi.fn()} isSubmitting={false} />);

    expect(screen.getByRole("button", { name: "Enviar contrato" })).toBeDisabled();
  });

  it("shows human-readable contract type labels", () => {
    render(<UploadForm onSubmit={vi.fn()} isSubmitting={false} />);

    expect(
      screen.getByRole("option", { name: "Minuta de terceiro" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: "Contrato assinado" }),
    ).toBeInTheDocument();
  });

  it("disables the inputs and shows a busy label while submitting", () => {
    render(<UploadForm onSubmit={vi.fn()} isSubmitting />);

    expect(screen.getByLabelText("Titulo do contrato")).toBeDisabled();
    expect(screen.getByLabelText("Referencia externa")).toBeDisabled();
    expect(screen.getByLabelText("Tipo de contrato")).toBeDisabled();
    expect(screen.getByRole("button", { name: "Processando..." })).toBeDisabled();
  });
});
```

- [ ] **Step 2: Run the targeted upload-form tests to verify they fail**

Run: `cd web && npm run test -- src/features/contracts/components/upload-form.test.tsx`
Expected: FAIL because the current form still exposes raw enum labels and does not disable all controls while submitting.

- [ ] **Step 3: Implement the refined form structure and styles**

In `upload-form.tsx`:
- keep the same submission contract
- replace raw enum copy with human-readable labels
- disable inputs while `isSubmitting`
- add a stronger file-upload presentation with helper copy
- keep the submit CTA text aligned with the guided flow

Minimal direction:

```tsx
const contractTypeOptions = [
  { value: "third_party_draft", label: "Minuta de terceiro" },
  { value: "signed_contract", label: "Contrato assinado" },
] as const;
```

```tsx
<button disabled={isSubmitting || !file} type="submit">
  {isSubmitting ? "Processando..." : "Enviar contrato"}
</button>
```

Use `upload-form.module.css` for field grouping, file surface, and CTA styling. Keep the prop surface unchanged so `ContractsScreen` does not need a new data contract.

- [ ] **Step 4: Re-run the upload-form tests**

Run: `cd web && npm run test -- src/features/contracts/components/upload-form.test.tsx`
Expected: PASS with the new submit-state and copy assertions green.

- [ ] **Step 5: Commit the upload panel polish**

```bash
git add web/src/features/contracts/components/upload-form.tsx web/src/features/contracts/components/upload-form.test.tsx web/src/features/contracts/components/upload-form.module.css web/src/features/contracts/screens/contracts-screen.tsx web/src/features/contracts/screens/contracts-screen.module.css
git commit -m "feat: refine contracts upload panel"
```

### Task 4: Run full verification, sync Trello, and update project memory

**Files:**
- Modify: `.codex-memory/current-state.md`
- Modify: `.codex-memory/session-log.md`

- [ ] **Step 1: Run the full frontend test suite**

Run: `cd web && npm run test`
Expected: PASS with all Vitest tests green.

- [ ] **Step 2: Run the production build**

Run: `cd web && npm run build`
Expected: PASS with a successful Next.js build.

- [ ] **Step 3: Manually verify the contracts screen in desktop and mobile widths**

Run: `cd web && npm run dev -- --hostname 127.0.0.1 --port 3000`

Check in the browser:
- width around `1280px`: upload and session status share the top row cleanly
- width around `390px`: all blocks collapse into one column
- empty state copy looks intentional
- if the local upload flow is available, a real successful upload still shows summary before findings and text
- if the local upload flow is not available, use the passing Vitest success-state test as the evidence for the result hierarchy and keep the manual check focused on layout and empty state

Expected: no broken overflow, no overlapping controls, and the upload CTA remains the main focus of the page.

- [ ] **Step 4: Update the F1-B Trello checklist only after verified milestones**

After each verified milestone, mark the matching item on card `F1-B Redesenhar tela de contratos` as complete:
- `Alinhar contrato de upload com F1-A`
- `Redefinir a hierarquia visual da tela /contracts`
- `Resolver estados de loading, erro, vazio e sucesso`
- `Refinar a area de upload e os feedbacks visuais`
- `Validar UX em desktop e mobile`

Do not store API key or token in the repository. Use runtime secrets only.

- [ ] **Step 5: Update persistent memory for the completed task**

In `.codex-memory/current-state.md`, record:
- the new contracts-screen guided layout
- files changed
- verification actually run
- any residual risk marked `a confirmar`
- next project step after F1-B

In `.codex-memory/session-log.md`, add one short entry summarizing the work and verification evidence.

- [ ] **Step 6: Commit the memory update**

```bash
git add .codex-memory/current-state.md .codex-memory/session-log.md
git commit -m "docs: update memory after contracts redesign"
```
