import React from "react";

import styles from "../screens/contracts-screen.module.css";

export function ContractsHero() {
  return (
    <header className={styles.hero}>
      <p className={styles.eyebrow}>Mesa de analise</p>
      <h1 className={styles.heroTitle}>Triagem contratual com criterio juridico</h1>
      <p className={styles.heroDescription}>
        Suba um PDF para abrir a leitura inicial do dossie, registrar contexto e
        organizar a proxima rodada de analise juridica dentro do workspace
        compartilhado.
      </p>
    </header>
  );
}
