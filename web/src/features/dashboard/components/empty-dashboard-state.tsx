import Link from "next/link";
import React from "react";

import styles from "../screens/dashboard-screen.module.css";

export function EmptyDashboardState() {
  return (
    <section className={styles.emptyDashboardState}>
      <p className={styles.emptyDashboardEyebrow}>Sem snapshot runtime</p>
      <h2 className={styles.emptyDashboardTitle}>Dashboard indisponível no momento.</h2>
      <p className={styles.emptyDashboardBody}>
        Assim que o primeiro contrato entrar na mesa, este painel passa a resumir
        o portfólio, destacar marcos operacionais e expor o histórico de
        notificações numa leitura executiva única.
      </p>
      <Link className={styles.emptyDashboardCta} href="/contracts">
        Envie seu primeiro contrato
      </Link>
    </section>
  );
}
