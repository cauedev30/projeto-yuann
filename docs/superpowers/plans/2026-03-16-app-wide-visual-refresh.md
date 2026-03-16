# App-Wide Visual Refresh Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar o refresh visual aprovado para a home e para o app logado, criando um shell compartilhado e uma linguagem executiva consistente sem alterar contratos de API nem a logica central das features.

**Architecture:** Introduzir uma camada fina de layout compartilhado em `web/src/app/` e `web/src/components/`, mantendo dados e comportamento dentro de `features/*/screens`. O refresh deve ser guiado por TDD onde houver comportamento verificavel, usando `globals.css` para tokens base e primitives pequenas (`MarketingTopbar`, `AppShell`, `PageHeader`, `SurfaceCard`, `StatCard`, `EmptyState`) para evitar duplicacao entre home, dashboard e contracts.

**Tech Stack:** Next.js App Router, React 19, TypeScript, Vitest, Testing Library, CSS Modules, Playwright (`a confirmar` no setup atual)

---

## Workflow Notes
- Executar em worktree isolado com `@superpowers:using-git-worktrees` antes de implementar.
- Seguir `@superpowers:test-driven-development` em toda mudanca com comportamento observavel.
- Pedir review ao final da implementacao com `@superpowers:requesting-code-review` se o harness permitir.
- Antes de declarar conclusao, rodar verificacoes frescas com `@superpowers:verification-before-completion`.
- Nao expandir o escopo do placeholder em `web/src/app/(app)/contracts/[contractId]/page.tsx`; nesta iteracao ele so herda o shell e o novo enquadramento visual.
- `cd web && npm run e2e` continua `a confirmar` ate a remocao do hardcode Windows em `web/playwright.config.ts`; usar evidencias manuais responsivas se isso continuar bloqueado.
- Para manter YAGNI, `AppTopbar` e `AppSidebar` entram nesta iteracao como partes internas de `AppShell`, nao como arquivos separados.
- `StatusBadge` e `ActionBar` ficam explicitamente adiados ate aparecer duplicacao real entre telas; nao implementar por antecipacao.

## Planned File Structure
- Modify: `web/src/app/layout.tsx`
  - importar os estilos globais, ajustar `lang` e aplicar o wrapper raiz do frontend.
- Create: `web/src/app/globals.css`
  - definir tokens globais, fundo, superfícies, tipografia, links, botoes base e utilitarios de layout.
- Modify: `web/src/app/page.tsx`
  - transformar a rota `/` em uma home comercial com hero, secoes de valor e CTA para o workspace.
- Create: `web/src/app/page.test.tsx`
  - proteger a narrativa principal da home e os links essenciais.
- Create: `web/src/components/navigation/marketing-topbar.tsx`
  - renderizar a navegacao institucional da home.
- Create: `web/src/components/navigation/app-shell.tsx`
  - renderizar a estrutura compartilhada da area logada com topbar, navegacao primaria e area de conteudo.
- Create: `web/src/components/navigation/app-shell.module.css`
  - guardar layout, drawer mobile, sidebar desktop e comportamento responsivo do shell.
- Create: `web/src/components/navigation/app-shell.test.tsx`
  - proteger a estrutura minima de navegacao do shell.
- Create: `web/src/components/ui/page-header.tsx`
  - padronizar cabecalho de area logada.
- Create: `web/src/components/ui/surface-card.tsx`
  - padronizar blocos visuais de conteudo.
- Create: `web/src/components/ui/stat-card.tsx`
  - padronizar indicadores curtos do dashboard.
- Create: `web/src/components/ui/empty-state.tsx`
  - padronizar vazio e indisponibilidade.
- Create: `web/src/components/ui/ui-primitives.module.css`
  - concentrar estilos compartilhados das primitives.
- Create: `web/src/app/(app)/layout.tsx`
  - aplicar `AppShell` a todas as rotas logadas.
- Modify: `web/src/features/dashboard/screens/dashboard-screen.tsx`
  - usar `PageHeader`, `SurfaceCard`, `StatCard` e `EmptyState` sem mudar o fluxo de dados.
- Create: `web/src/features/dashboard/screens/dashboard-screen.module.css`
  - guardar composicao executiva do dashboard.
- Modify: `web/src/features/dashboard/screens/dashboard-screen.test.tsx`
  - proteger o novo enquadramento textual do dashboard com e sem snapshot.
- Modify: `web/src/features/dashboard/components/contracts-summary.tsx`
  - devolver somente a grade de indicadores usando `StatCard`.
- Modify: `web/src/features/dashboard/components/empty-dashboard-state.tsx`
  - delegar o estado vazio para `EmptyState`.
- Modify: `web/src/features/dashboard/components/events-timeline.tsx`
  - permitir reutilizacao dentro de `SurfaceCard` sem titulo duplicado.
- Modify: `web/src/features/notifications/components/notification-history.tsx`
  - permitir reutilizacao dentro de `SurfaceCard` sem titulo duplicado.
- Modify: `web/src/features/contracts/screens/contracts-screen.tsx`
  - alinhar a screen ao shell compartilhado e remover dependencias de viewport proprio.
- Modify: `web/src/features/contracts/screens/contracts-screen.module.css`
  - trocar tokens locais por tokens globais e ajustar espacamento para o shell novo.
- Modify: `web/src/features/contracts/components/contracts-hero.tsx`
  - alinhar a hero a linguagem executiva aprovada.
- Modify: `web/src/features/contracts/screens/contracts-screen.test.tsx`
  - manter cobertura de estados e proteger o texto principal apos o ajuste visual.
- Modify: `web/src/app/(app)/contracts/[contractId]/page.tsx`
  - enquadrar o placeholder atual com `PageHeader` e `SurfaceCard`.
- Create: `web/src/app/(app)/contracts/[contractId]/page.test.tsx`
  - proteger a permanencia do placeholder dentro da nova moldura.
- Modify: `.codex-memory/current-state.md`
  - registrar o estado verificado apos implementar o refresh.
- Modify: `.codex-memory/session-log.md`
  - registrar o resumo da sessao.

## Chunk 1: Shared Foundation and Marketing Entry

### Task 1: Protect and rebuild the marketing home before touching shared styles

**Files:**
- Modify: `web/src/app/page.tsx`
- Create: `web/src/app/page.test.tsx`
- Create: `web/src/components/navigation/marketing-topbar.tsx`

- [ ] **Step 1: Write the failing test for the marketing home**

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "./page";

describe("HomePage", () => {
  it("renders the commercial hero, value sections and workspace CTAs", () => {
    render(<HomePage />);

    expect(
      screen.getByRole("heading", {
        name: "Governanca contratual para times de expansao",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Entrar no workspace" }),
    ).toHaveAttribute("href", "/dashboard");
    expect(
      screen.getByRole("heading", { name: "Do intake ao acompanhamento" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Upload e triagem inicial")).toBeInTheDocument();
    expect(screen.getByText("Monitoramento de eventos")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run the targeted home test to verify it fails**

Run: `cd web && npm run test -- src/app/page.test.tsx`
Expected: FAIL because `web/src/app/page.tsx` ainda expõe apenas o placeholder "LegalTech MVP".

- [ ] **Step 3: Implement the minimal marketing home and topbar**

Create `MarketingTopbar` with a small brand block and two links:

```tsx
import Link from "next/link";

export function MarketingTopbar() {
  return (
    <header>
      <Link href="/">YUANN Platform</Link>
      <nav aria-label="Navegacao institucional">
        <Link href="#produto">Produto</Link>
        <Link href="#fluxo">Fluxo</Link>
        <Link href="/dashboard">Entrar no workspace</Link>
      </nav>
    </header>
  );
}
```

Replace `web/src/app/page.tsx` with a marketing structure that includes:
- `MarketingTopbar`
- hero with `Governanca contratual para times de expansao`
- a section `Do intake ao acompanhamento`
- cards or blocks for `Upload e triagem inicial`, `Politicas e findings`, `Monitoramento de eventos`
- primary CTA to `/dashboard`

- [ ] **Step 4: Run the targeted home test to verify it passes**

Run: `cd web && npm run test -- src/app/page.test.tsx`
Expected: PASS with 1 passing test.

- [ ] **Step 5: Commit the marketing home baseline**

```bash
git add web/src/app/page.tsx web/src/app/page.test.tsx web/src/components/navigation/marketing-topbar.tsx
git commit -m "feat: add marketing home baseline"
```

### Task 2: Add global tokens and shared UI primitives for the refresh

**Files:**
- Modify: `web/src/app/layout.tsx`
- Create: `web/src/app/globals.css`
- Create: `web/src/components/ui/page-header.tsx`
- Create: `web/src/components/ui/surface-card.tsx`
- Create: `web/src/components/ui/stat-card.tsx`
- Create: `web/src/components/ui/empty-state.tsx`
- Create: `web/src/components/ui/ui-primitives.module.css`
- Test: `web/src/app/page.test.tsx`

- [ ] **Step 1: Extend the home test to assert the new root language and CTA framing**

Add one assertion that the page renders the primary CTA copy and prepare `layout.tsx` for `lang="pt-BR"`:

```tsx
expect(screen.getByText("Uma interface clara para revisar contratos, risco e proximas acoes.")).toBeInTheDocument();
```

Then add a small layout contract test inline or via `renderToStaticMarkup`:

```tsx
import { renderToStaticMarkup } from "react-dom/server";
import RootLayout from "./layout";

it("sets the application language to pt-BR", () => {
  const html = renderToStaticMarkup(
    <RootLayout>
      <div>child</div>
    </RootLayout>,
  );

  expect(html).toContain('lang="pt-BR"');
});
```

- [ ] **Step 2: Run the targeted tests to verify they fail**

Run: `cd web && npm run test -- src/app/page.test.tsx`
Expected: FAIL because `layout.tsx` still uses `lang="en"` and no global visual baseline exists.

- [ ] **Step 3: Implement the minimal global visual foundation**

Update `web/src/app/layout.tsx` to import `./globals.css` and set `lang="pt-BR"`:

```tsx
import "./globals.css";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="app-root">{children}</body>
    </html>
  );
}
```

Create `globals.css` with:
- app-level color tokens (`--bg`, `--surface`, `--line`, `--brand-blue`, `--brand-green`)
- typography defaults
- body background and text color
- shared button/link utility classes used by the home

Add minimal shared primitives:

```tsx
export function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description?: string;
}) {
  return (
    <header className={styles.pageHeader}>
      <p className={styles.eyebrow}>{eyebrow}</p>
      <h1>{title}</h1>
      {description ? <p className={styles.description}>{description}</p> : null}
    </header>
  );
}
```

```tsx
export function SurfaceCard({
  children,
  title,
}: {
  children: React.ReactNode;
  title?: string;
}) {
  return (
    <section className={styles.surfaceCard}>
      {title ? <h2>{title}</h2> : null}
      {children}
    </section>
  );
}
```

- [ ] **Step 4: Re-run the targeted tests after the global foundation**

Run: `cd web && npm run test -- src/app/page.test.tsx`
Expected: PASS with the home assertions and the `pt-BR` root-layout contract green.

- [ ] **Step 5: Commit the shared foundation**

```bash
git add web/src/app/layout.tsx web/src/app/globals.css web/src/components/ui/page-header.tsx web/src/components/ui/surface-card.tsx web/src/components/ui/stat-card.tsx web/src/components/ui/empty-state.tsx web/src/components/ui/ui-primitives.module.css web/src/app/page.test.tsx
git commit -m "feat: add shared visual foundation"
```

## Chunk 2: Logged App Shell and Feature Integration

### Task 3: Create the logged app shell before adapting any feature screen

**Files:**
- Create: `web/src/components/navigation/app-shell.tsx`
- Create: `web/src/components/navigation/app-shell.module.css`
- Create: `web/src/components/navigation/app-shell.test.tsx`
- Create: `web/src/app/(app)/layout.tsx`

- [ ] **Step 1: Write the failing test for the shared logged shell**

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AppShell } from "./app-shell";

describe("AppShell", () => {
  it("renders the primary workspace navigation and the content region", () => {
    render(
      <AppShell>
        <div>Conteudo interno</div>
      </AppShell>,
    );

    expect(
      screen.getByRole("navigation", { name: "Navegacao principal do workspace" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute(
      "href",
      "/dashboard",
    );
    expect(screen.getByRole("link", { name: "Contracts" })).toHaveAttribute(
      "href",
      "/contracts",
    );
    expect(screen.getByText("Conteudo interno")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run the shell test to verify it fails**

Run: `cd web && npm run test -- src/components/navigation/app-shell.test.tsx`
Expected: FAIL because `AppShell` and `web/src/app/(app)/layout.tsx` do not exist yet.

- [ ] **Step 3: Implement the minimal shell and apply it to `/(app)`**

Create `AppShell` with:
- topbar containing `YUANN Platform`
- primary nav links `Dashboard` and `Contracts`
- mobile collapsible nav using semantic `<details>`
- content slot for `children`

```tsx
import Link from "next/link";
import type { ReactNode } from "react";
import styles from "./app-shell.module.css";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <Link href="/" className={styles.brand}>YUANN Platform</Link>
        <nav aria-label="Navegacao principal do workspace">
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/contracts">Contracts</Link>
        </nav>
      </aside>
      <div className={styles.contentFrame}>
        <header className={styles.topbar}>
          <details className={styles.mobileNav}>
            <summary>Abrir navegacao</summary>
            <nav aria-label="Navegacao principal do workspace">
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/contracts">Contracts</Link>
            </nav>
          </details>
        </header>
        <main className={styles.content}>{children}</main>
      </div>
    </div>
  );
}
```

Then create `web/src/app/(app)/layout.tsx`:

```tsx
import type { ReactNode } from "react";
import { AppShell } from "@/components/navigation/app-shell";

export default function LoggedAppLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
```

- [ ] **Step 4: Re-run the shell test and a full build**

Run: `cd web && npm run test -- src/components/navigation/app-shell.test.tsx`
Expected: PASS.

Run: `cd web && npm run build`
Expected: PASS with the new `/(app)/layout.tsx` wired into the router.

- [ ] **Step 5: Commit the logged shell**

```bash
git add web/src/components/navigation/app-shell.tsx web/src/components/navigation/app-shell.module.css web/src/components/navigation/app-shell.test.tsx web/src/app/\(app\)/layout.tsx
git commit -m "feat: add shared logged app shell"
```

### Task 4: Adapt the dashboard to the shared primitives without changing data flow

**Files:**
- Modify: `web/src/features/dashboard/screens/dashboard-screen.tsx`
- Create: `web/src/features/dashboard/screens/dashboard-screen.module.css`
- Modify: `web/src/features/dashboard/screens/dashboard-screen.test.tsx`
- Modify: `web/src/features/dashboard/components/contracts-summary.tsx`
- Modify: `web/src/features/dashboard/components/empty-dashboard-state.tsx`
- Modify: `web/src/features/dashboard/components/events-timeline.tsx`
- Modify: `web/src/features/notifications/components/notification-history.tsx`

- [ ] **Step 1: Write the failing dashboard tests for the executive framing**

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { buildDashboardSnapshotFixture } from "../fixtures/dashboard-snapshot";
import { DashboardScreen } from "./dashboard-screen";

describe("DashboardScreen", () => {
  it("frames the unavailable state with an executive header", () => {
    render(<DashboardScreen snapshot={null} />);

    expect(screen.getByText("Portifolio contratual")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Dashboard de renovacoes" })).toBeInTheDocument();
    expect(screen.getByText("Dashboard indisponivel no momento.")).toBeInTheDocument();
  });

  it("renders summary, timeline and notification blocks when a snapshot exists", () => {
    render(<DashboardScreen snapshot={buildDashboardSnapshotFixture()} />);

    expect(screen.getByText("Resumo do portifolio")).toBeInTheDocument();
    expect(screen.getByText("Timeline de eventos")).toBeInTheDocument();
    expect(screen.getByText("Historico de notificacoes")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run the dashboard tests to verify they fail**

Run: `cd web && npm run test -- src/features/dashboard/screens/dashboard-screen.test.tsx`
Expected: FAIL because the current dashboard has no shared header or executive section framing.

- [ ] **Step 3: Implement the dashboard with shared primitives**

Update `DashboardScreen` to use:
- `PageHeader` for the top section
- `SurfaceCard` around summary, timeline and notification history
- `ContractsSummary` implemented as a small `StatCard` grid
- `EmptyDashboardState` delegating to shared `EmptyState`
- `EventsTimeline` e `NotificationHistory` com `showTitle={false}` quando renderizados dentro dos cards

Minimal target structure:

```tsx
<main className={styles.page}>
  <PageHeader
    eyebrow="Portifolio contratual"
    title="Dashboard de renovacoes"
    description="Acompanhe contratos ativos, eventos e sinais de risco sem mascarar a ausencia de dados runtime."
  />

  {snapshot ? (
    <>
      <SurfaceCard title="Resumo do portifolio">
        <ContractsSummary summary={snapshot.summary} />
      </SurfaceCard>
      <SurfaceCard title="Timeline de eventos">
        <EventsTimeline events={snapshot.events} showTitle={false} />
      </SurfaceCard>
      <SurfaceCard title="Historico de notificacoes">
        <NotificationHistory items={snapshot.notifications} showTitle={false} />
      </SurfaceCard>
    </>
  ) : (
    <EmptyDashboardState />
  )}
</main>
```

- [ ] **Step 4: Re-run the dashboard tests and one focused E2E spec if available**

Run: `cd web && npm run test -- src/features/dashboard/screens/dashboard-screen.test.tsx`
Expected: PASS.

Run: `cd web && npm run test -- src/features/notifications/components/notification-history.test.tsx src/features/dashboard/components/events-timeline.test.tsx`
Expected: PASS to confirm subcomponents still behave correctly inside the new framing.

- [ ] **Step 5: Commit the dashboard adaptation**

```bash
git add web/src/features/dashboard/screens/dashboard-screen.tsx web/src/features/dashboard/screens/dashboard-screen.module.css web/src/features/dashboard/screens/dashboard-screen.test.tsx web/src/features/dashboard/components/contracts-summary.tsx web/src/features/dashboard/components/empty-dashboard-state.tsx web/src/features/dashboard/components/events-timeline.tsx web/src/features/notifications/components/notification-history.tsx
git commit -m "feat: adapt dashboard to shared shell primitives"
```

### Task 5: Align contracts and the detail placeholder to the new shell

**Files:**
- Modify: `web/src/features/contracts/screens/contracts-screen.tsx`
- Modify: `web/src/features/contracts/screens/contracts-screen.module.css`
- Modify: `web/src/features/contracts/components/contracts-hero.tsx`
- Modify: `web/src/features/contracts/screens/contracts-screen.test.tsx`
- Modify: `web/src/app/(app)/contracts/[contractId]/page.tsx`
- Create: `web/src/app/(app)/contracts/[contractId]/page.test.tsx`

- [ ] **Step 1: Write the failing detail-page test and extend the contracts screen assertions**

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ContractDetailPage from "./page";

describe("ContractDetailPage", () => {
  it("keeps the placeholder content inside the shared contracts framing", async () => {
    const page = await ContractDetailPage({
      params: Promise.resolve({ contractId: "CTR-001" }),
    });

    render(page);

    expect(screen.getByText("Contracts")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "CTR-001" })).toBeInTheDocument();
    expect(
      screen.getByText("A timeline detalhada e os findings persistidos entram na proxima iteracao."),
    ).toBeInTheDocument();
  });
});
```

In `contracts-screen.test.tsx`, add one assertion that the hero copy remains present after the visual alignment:

```tsx
expect(scope.getByText("Governanca contratual")).toBeInTheDocument();
```

- [ ] **Step 2: Run the targeted contracts tests to verify they fail**

Run: `cd web && npm run test -- src/features/contracts/screens/contracts-screen.test.tsx 'src/app/(app)/contracts/[contractId]/page.test.tsx'`
Expected: FAIL because the detail route has no shared framing and the contracts screen still assumes a standalone viewport shell.

- [ ] **Step 3: Implement the shell-aligned contracts styling**

Update `contracts-screen.module.css` to:
- drop `min-height: 100vh`
- replace feature-local page background ownership with spacing that works inside `AppShell`
- reuse global color tokens instead of a completely separate palette
- keep the existing upload/result hierarchy intact

Update `contracts-screen.tsx` and `contracts-hero.tsx` only as needed to:
- preserve the guided flow
- keep the hero consistent with the new executive tone
- avoid nested viewport or duplicated chrome assumptions

Update the detail placeholder:

```tsx
import { PageHeader } from "@/components/ui/page-header";
import { SurfaceCard } from "@/components/ui/surface-card";

export default async function ContractDetailPage({ params }: ContractDetailPageProps) {
  const { contractId } = await params;

  return (
    <main>
      <PageHeader
        eyebrow="Contracts"
        title={contractId}
        description="Detalhe do contrato ainda em placeholder, mas agora dentro da moldura compartilhada do workspace."
      />
      <SurfaceCard>
        <p>A timeline detalhada e os findings persistidos entram na proxima iteracao.</p>
      </SurfaceCard>
    </main>
  );
}
```

- [ ] **Step 4: Re-run the targeted contracts tests and the full unit suite**

Run: `cd web && npm run test -- src/features/contracts/screens/contracts-screen.test.tsx 'src/app/(app)/contracts/[contractId]/page.test.tsx'`
Expected: PASS.

Run: `cd web && npm run test`
Expected: PASS with all Vitest suites green.

- [ ] **Step 5: Commit the contracts alignment**

```bash
git add web/src/features/contracts/screens/contracts-screen.tsx web/src/features/contracts/screens/contracts-screen.module.css web/src/features/contracts/components/contracts-hero.tsx web/src/features/contracts/screens/contracts-screen.test.tsx web/src/app/\(app\)/contracts/\[contractId\]/page.tsx web/src/app/\(app\)/contracts/\[contractId\]/page.test.tsx
git commit -m "feat: align contracts with shared product shell"
```

### Task 6: Verification, responsive QA, and project memory updates

**Files:**
- Modify: `.codex-memory/current-state.md`
- Modify: `.codex-memory/session-log.md`

- [ ] **Step 1: Run the final automated verification**

Run: `cd web && npm run test`
Expected: PASS.

Run: `cd web && npm run build`
Expected: PASS.

- [ ] **Step 2: Attempt E2E verification and record the real outcome**

Run: `cd web && npm run e2e`
Expected: either PASS if `web/playwright.config.ts` was fixed separately before this task, or FAIL for the known Windows-specific backend command. Do not hide the result; record it explicitly as `a confirmar` if still blocked.

- [ ] **Step 3: Perform manual responsive QA on the primary routes**

Check in desktop and mobile widths:
- `/`
- `/dashboard`
- `/contracts`
- `/contracts/CTR-001`

Record evidence for:
- home CTA clarity
- sidebar or mobile nav behavior
- honest dashboard empty state
- contracts upload CTA still obvious
- detail placeholder visually subordinate to the module shell

- [ ] **Step 4: Update project memory**

Update `.codex-memory/current-state.md` with:
- files changed
- verification evidence
- residual risk around Playwright if still blocked
- next step after the refresh

Append a short entry to `.codex-memory/session-log.md` summarizing the implementation.

- [ ] **Step 5: Commit the verification and memory updates**

```bash
git add .codex-memory/current-state.md .codex-memory/session-log.md
git commit -m "docs: record app-wide visual refresh verification"
```
