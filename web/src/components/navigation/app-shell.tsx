import React, { type ReactNode } from "react";
import Link from "next/link";

import styles from "./app-shell.module.css";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className={styles.shell}>
      <a className={styles.skipLink} href="#main-content">
        Pular para o conteudo principal
      </a>
      <aside className={styles.sidebar}>
        <Link aria-label="LegalTech" className={styles.brand} href="/">
          <span aria-hidden="true" className={styles.brandMark}>
            LT
          </span>
          <span className={styles.brandCopy}>
            <strong className={styles.brandName}>LegalTech</strong>
            <span className={styles.brandMeta}>Governanca contratual</span>
          </span>
        </Link>

        <div className={styles.sidebarIntro}>
          <p className={styles.sidebarEyebrow}>Workspace ativo</p>
          <p className={styles.sidebarStatement}>
            Criterio juridico, ritmo operacional e contexto compartilhado.
          </p>
        </div>

        <nav aria-label="Navegacao principal do workspace" className={styles.sidebarNav}>
          <Link aria-label="Dashboard" className={styles.navLink} href="/dashboard">
            <span className={styles.navTitle}>Dashboard</span>
            <small aria-hidden="true" className={styles.navMeta}>
              Portfolio, eventos e notificacoes
            </small>
          </Link>
          <Link aria-label="Contracts" className={styles.navLink} href="/contracts">
            <span className={styles.navTitle}>Contracts</span>
            <small aria-hidden="true" className={styles.navMeta}>
              Intake, triagem e findings
            </small>
          </Link>
        </nav>

        <div className={styles.sidebarMeta}>
          <strong>Legal operations</strong>
          <span>Dashboard e contracts agora dividem o mesmo pulso visual.</span>
        </div>
      </aside>

      <div className={styles.contentFrame}>
        <header className={styles.topbar}>
          <details className={styles.mobileNav}>
            <summary className={styles.mobileSummary}>Abrir navegacao</summary>
            <nav aria-label="Navegacao movel do workspace" className={styles.mobilePanel}>
              <Link aria-label="Dashboard" className={styles.navLink} href="/dashboard">
                <span className={styles.navTitle}>Dashboard</span>
                <small aria-hidden="true" className={styles.navMeta}>
                  Portfolio, eventos e notificacoes
                </small>
              </Link>
              <Link aria-label="Contracts" className={styles.navLink} href="/contracts">
                <span className={styles.navTitle}>Contracts</span>
                <small aria-hidden="true" className={styles.navMeta}>
                  Intake, triagem e findings
                </small>
              </Link>
            </nav>
          </details>

          <div className={styles.topbarCopy}>
            <p className={styles.topbarEyebrow}>Workspace juridico</p>
            <strong className={styles.topbarTitle}>
              Workspace juridico para contratos, risco e decisoes em andamento.
            </strong>
          </div>

          <div className={styles.topbarMeta}>
            <span className={styles.topbarMetaLabel}>Camada compartilhada</span>
            <strong className={styles.topbarMetaValue}>
              Leitura operacional com acabamento editorial
            </strong>
          </div>
        </header>

        <main className={styles.content} id="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}
