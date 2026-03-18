import React from "react";

import styles from "../screens/contracts-screen.module.css";

type SessionStatusCardProps = {
  state: "empty" | "loading" | "error" | "success";
  message: string;
};

const stateMeta = {
  empty: {
    title: "Pronto para iniciar",
    badge: "Aguardando documento",
    description: "Nenhum arquivo enviado nesta sessao. O upload do contrato iniciara a triagem e liberara o resumo executivo.",
    tone: styles.sessionToneEmpty,
  },
  loading: {
    title: "Estado da sessao",
    badge: "Em processamento",
    description: "O contrato esta sendo processado. Mantenha esta tela aberta para revisar o retorno assim que a triagem terminar.",
    tone: styles.sessionToneLoading,
  },
  error: {
    title: "Estado da sessao",
    badge: "Falha no envio",
    description: "A submissao nao terminou como esperado. Revise os dados e tente novamente sem perder o contexto da sessao.",
    tone: styles.sessionToneError,
  },
  success: {
    title: "Estado da sessao",
    badge: "Triagem concluida",
    description: "O contrato ja passou pela triagem inicial e os blocos abaixo estao prontos para leitura operacional.",
    tone: styles.sessionToneSuccess,
  },
} as const;

export function SessionStatusCard({ state, message }: SessionStatusCardProps) {
  const meta = stateMeta[state];

  return (
    <section className={`${styles.panel} ${styles.sessionCard} ${meta.tone}`}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.panelEyebrow}>{meta.badge}</p>
          <h2 className={styles.sectionTitle}>{meta.title}</h2>
        </div>
        <span className={styles.statusChip}>{meta.badge}</span>
      </div>

      <p className={styles.sessionDescription}>{meta.description}</p>
      <p className={styles.sessionMessage} role={state === "error" ? "alert" : undefined}>
        {message}
      </p>
    </section>
  );
}
