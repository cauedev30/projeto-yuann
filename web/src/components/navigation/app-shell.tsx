"use client";

import React, { type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import styles from "./app-shell.module.css";

type AppShellProps = {
  children: ReactNode;
};

type TopbarContext = {
  title: string;
  subtitle: string;
};

function getTopbarContext(pathname: string): TopbarContext {
  if (pathname.startsWith("/contracts/")) {
    return { title: "Contracts", subtitle: "Detalhe do contrato" };
  }

  if (pathname.startsWith("/contracts")) {
    return { title: "Contracts", subtitle: "Intake e triagem" };
  }

  if (pathname.startsWith("/dashboard")) {
    return { title: "Dashboard", subtitle: "Governanca contratual" };
  }

  return { title: "Workspace", subtitle: "Governanca contratual" };
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const topbar = getTopbarContext(pathname);

  function navLinkClass(href: string): string {
    const isActive = pathname.startsWith(href);
    return isActive ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink;
  }

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

        <nav aria-label="Navegacao principal do workspace" className={styles.sidebarNav}>
          <Link aria-label="Dashboard" className={navLinkClass("/dashboard")} href="/dashboard">
            <span className={styles.navTitle}>Dashboard</span>
            <small aria-hidden="true" className={styles.navMeta}>
              Portfolio, eventos e notificacoes
            </small>
          </Link>
          <Link aria-label="Contracts" className={navLinkClass("/contracts")} href="/contracts">
            <span className={styles.navTitle}>Contracts</span>
            <small aria-hidden="true" className={styles.navMeta}>
              Intake, triagem e findings
            </small>
          </Link>
        </nav>
      </aside>

      <div className={styles.contentFrame}>
        <header className={styles.topbar}>
          <details className={styles.mobileNav}>
            <summary className={styles.mobileSummary}>Abrir navegacao</summary>
            <nav aria-label="Navegacao movel do workspace" className={styles.mobilePanel}>
              <Link aria-label="Dashboard" className={navLinkClass("/dashboard")} href="/dashboard">
                <span className={styles.navTitle}>Dashboard</span>
                <small aria-hidden="true" className={styles.navMeta}>
                  Portfolio, eventos e notificacoes
                </small>
              </Link>
              <Link aria-label="Contracts" className={navLinkClass("/contracts")} href="/contracts">
                <span className={styles.navTitle}>Contracts</span>
                <small aria-hidden="true" className={styles.navMeta}>
                  Intake, triagem e findings
                </small>
              </Link>
            </nav>
          </details>

          <div className={styles.topbarCopy}>
            <p className={styles.topbarEyebrow}>{topbar.title}</p>
            <strong className={styles.topbarTitle}>{topbar.subtitle}</strong>
          </div>
        </header>

        <main className={styles.content} id="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}
