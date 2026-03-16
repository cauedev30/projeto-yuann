import React, { type ReactNode } from "react";
import Link from "next/link";

import styles from "./app-shell.module.css";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <Link className={styles.brand} href="/">
          YUANN Platform
        </Link>

        <nav aria-label="Navegacao principal do workspace" className={styles.sidebarNav}>
          <Link className={styles.navLink} href="/dashboard">
            Dashboard
          </Link>
          <Link className={styles.navLink} href="/contracts">
            Contracts
          </Link>
        </nav>

        <div className={styles.sidebarMeta}>
          <strong>Workspace operacional</strong>
          <span>Dashboard e contracts agora dividem a mesma camada visual.</span>
        </div>
      </aside>

      <div className={styles.contentFrame}>
        <header className={styles.topbar}>
          <details className={styles.mobileNav}>
            <summary className={styles.mobileSummary}>Abrir navegacao</summary>
            <nav aria-label="Navegacao movel do workspace" className={styles.mobilePanel}>
              <Link className={styles.navLink} href="/dashboard">
                Dashboard
              </Link>
              <Link className={styles.navLink} href="/contracts">
                Contracts
              </Link>
            </nav>
          </details>

          <div className={styles.topbarCopy}>
            Camada compartilhada para fluxos juridicos e operacionais.
          </div>
        </header>

        <main className={styles.content}>{children}</main>
      </div>
    </div>
  );
}
