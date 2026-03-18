import React from "react";

import styles from "../screens/contracts-screen.module.css";

export function ContractsHero() {
  return (
    <header className={styles.hero}>
      <p className={styles.eyebrow}>Contratos</p>
      <h1 className={styles.heroTitle}>Analise de contratos</h1>
      <p className={styles.heroDescription}>
        Suba um PDF para iniciar a triagem e registrar o contrato no workspace.
      </p>
    </header>
  );
}
