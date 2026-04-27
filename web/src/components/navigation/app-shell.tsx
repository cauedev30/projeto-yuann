"use client";

import React, { type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "../../contexts/auth-context";
import { NotificationBadge } from "../../features/notifications/components/notification-badge";
import { ScrollToBottom } from "../ui/scroll-to-bottom";
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
    return { title: "Contratos", subtitle: "Detalhe do contrato" };
  }

  if (pathname.startsWith("/contracts")) {
    return { title: "Contratos", subtitle: "Entrada e triagem" };
  }

  if (pathname.startsWith("/dashboard")) {
    return { title: "Dashboard", subtitle: "Governanca contratual" };
  }

  if (pathname.startsWith("/acervo")) {
    return { title: "Acervo", subtitle: "Contratos ativos" };
  }

  if (pathname.startsWith("/historico")) {
    return { title: "Histórico", subtitle: "Contratos analisados" };
  }

  return { title: "Espaço de trabalho", subtitle: "Governanca contratual" };
}

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const topbar = getTopbarContext(pathname);
  const { logout, user } = useAuth();
  const isAdmin = user?.role === "admin";

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
        <Link aria-label="LegalBoard" className={styles.brand} href="/">
          <img
            alt=""
            className={styles.brandLogo}
            height={40}
            src="/logo.png"
            width={40}
          />
          <span className={styles.brandCopy}>
            <strong className={styles.brandName}>LegalBoard</strong>
            <span className={styles.brandMeta}>Governanca contratual</span>
          </span>
        </Link>

        <nav aria-label="Navegação principal do workspace" className={styles.sidebarNav}>
          <Link aria-label="Dashboard" className={navLinkClass("/dashboard")} href="/dashboard">
            <span className={styles.navTitle}>Dashboard</span>
            <small aria-hidden="true" className={styles.navMeta}>
              Resumo, eventos e notificações
            </small>
          </Link>
          <Link aria-label="Acervo" className={navLinkClass("/acervo")} href="/acervo">
            <span className={styles.navTitle}>Acervo</span>
            <small aria-hidden="true" className={styles.navMeta}>
              Contratos ativos
            </small>
          </Link>
          <Link aria-label="Histórico" className={navLinkClass("/historico")} href="/historico">
            <span className={styles.navTitle}>Histórico</span>
            <small aria-hidden="true" className={styles.navMeta}>
              Contratos analisados
            </small>
          </Link>
          <Link aria-label="Contratos" className={navLinkClass("/contracts")} href="/contracts">
            <span className={styles.navTitle}>Contratos</span>
            <small aria-hidden="true" className={styles.navMeta}>
              Entrada, triagem e achados
            </small>
          </Link>
          {isAdmin && (
            <Link aria-label="Admin" className={navLinkClass("/admin")} href="/admin/usuarios">
              <span className={styles.navTitle}>Admin</span>
              <small aria-hidden="true" className={styles.navMeta}>
                Gerenciar usuários
              </small>
            </Link>
          )}
        </nav>

        <div className={styles.sidebarFooter}>
          {user ? (
            <p className={styles.userName}>{user.fullName}</p>
          ) : null}
          <button
            className={styles.logoutButton}
            onClick={logout}
            type="button"
          >
            Sair
          </button>
        </div>
      </aside>

      <div className={styles.contentFrame}>
        <header className={styles.topbar}>
          <details className={styles.mobileNav}>
            <summary className={styles.mobileSummary}>Abrir navegação</summary>
            <nav aria-label="Navegação móvel do workspace" className={styles.mobilePanel}>
              <Link aria-label="Dashboard" className={navLinkClass("/dashboard")} href="/dashboard">
                <span className={styles.navTitle}>Dashboard</span>
                <small aria-hidden="true" className={styles.navMeta}>
                  Resumo, eventos e notificações
                </small>
              </Link>
              <Link aria-label="Acervo" className={navLinkClass("/acervo")} href="/acervo">
                <span className={styles.navTitle}>Acervo</span>
                <small aria-hidden="true" className={styles.navMeta}>
                  Contratos ativos
                </small>
              </Link>
              <Link aria-label="Histórico" className={navLinkClass("/historico")} href="/historico">
                <span className={styles.navTitle}>Histórico</span>
                <small aria-hidden="true" className={styles.navMeta}>
                  Contratos analisados
                </small>
              </Link>
              <Link aria-label="Contratos" className={navLinkClass("/contracts")} href="/contracts">
                <span className={styles.navTitle}>Contratos</span>
                <small aria-hidden="true" className={styles.navMeta}>
                  Entrada, triagem e achados
                </small>
              </Link>
              {isAdmin && (
                <Link aria-label="Admin" className={navLinkClass("/admin")} href="/admin/usuarios">
                  <span className={styles.navTitle}>Admin</span>
                  <small aria-hidden="true" className={styles.navMeta}>
                    Gerenciar usuários
                  </small>
                </Link>
              )}
            </nav>
            <div className={styles.mobileLogout}>
              {user ? (
                <p className={styles.userName}>{user.fullName}</p>
              ) : null}
              <button
                className={styles.logoutButton}
                onClick={logout}
                type="button"
              >
                Sair
              </button>
            </div>
          </details>

          <div className={styles.topbarCopy}>
            <p className={styles.topbarEyebrow}>{topbar.title}</p>
            <strong className={styles.topbarTitle}>{topbar.subtitle}</strong>
          </div>
          <NotificationBadge />
        </header>

        <main className={styles.content} id="main-content">
          {children}
        </main>
      </div>
      <ScrollToBottom />
    </div>
  );
}
