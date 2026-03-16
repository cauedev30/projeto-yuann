import React from "react";

import styles from "../screens/contracts-screen.module.css";

export function ContractsHero() {
  return (
    <header className={styles.hero}>
      <p className={styles.eyebrow}>Governanca contratual</p>
      <h1 className={styles.heroTitle}>Envie um contrato para triagem inicial</h1>
      <p className={styles.heroDescription}>
        Suba um PDF para revisar a sessao atual, identificar o nivel de risco inicial e
        organizar a proxima analise juridica.
      </p>
    </header>
  );
}
