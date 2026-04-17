"use client";

import React, { useRef, useState } from "react";

import type { ContractFinding } from "../../../entities/contracts/model";
import styles from "./clause-stepper.module.css";

const CANONICAL_NAMES: Record<string, string> = {
  OBJETO_E_VIABILIDADE: "Objeto e Viabilidade",
  EXCLUSIVIDADE: "Exclusividade",
  OBRAS_E_ADAPTACOES: "Obras e Adaptações",
  CESSAO_E_SUBLOCACAO: "Cessão e Sublocação",
  PRAZO_E_RENOVACAO: "Prazo e Renovação",
  COMUNICACAO_E_PENALIDADES: "Comunicação e Penalidades",
  OBRIGACAO_DE_NAO_FAZER: "Obrigação de Não Fazer",
  VISTORIA_E_ACESSO: "Vistoria e Acesso",
  ASSINATURA_E_FORMA: "Assinatura e Forma",
};

type ClauseStepperProps = {
  findings: ContractFinding[];
  context?: "acervo" | "historico" | "contracts";
  riskScore?: number | null;
};

function classificationFromStatus(status: string): string {
  if (status === "conforme") return "adequada";
  if (status === "critical") return "conflitante";
  return "risco_medio";
}

function classificationLabel(cls: string): string {
  const labels: Record<string, string> = {
    adequada: "Adequada",
    risco_medio: "Risco médio",
    ausente: "Ausente",
    conflitante: "Conflitante",
  };
  return labels[cls] || cls;
}

function VerdictPanel({ findings, riskScore }: { findings: ContractFinding[]; riskScore: number | null }) {
  const criticals = findings.filter((f) => f.status === "critical").length;
  const attentions = findings.filter((f) => f.status === "attention").length;
  const conforme = findings.length - criticals - attentions;

  return (
    <div className={styles.verdictPanel}>
      <h3 className={styles.verdictTitle}>Veredito Final</h3>
      {riskScore !== null && (
        <p className={styles.verdictScore}>Score de risco: {riskScore}/100</p>
      )}
      <p>{criticals} críticos · {attentions} atenção · {conforme} conforme</p>
      {criticals === 0 && attentions === 0 ? (
        <p className={styles.verdictConforme}>O contrato está em conformidade com o padrão da franquia.</p>
      ) : (
        <p className={styles.verdictAtencao}>O contrato apresenta pontos que requerem atenção.</p>
      )}
    </div>
  );
}

export function ClauseStepper({ findings, context = "contracts", riskScore }: ClauseStepperProps) {
  const [index, setIndex] = useState(0);
  const [hasReadClause, setHasReadClause] = useState(false);
  const clauseBodyRef = useRef<HTMLDivElement>(null);
  const showVerdict = index >= findings.length;

  if (showVerdict) {
    return <VerdictPanel findings={findings} riskScore={riskScore ?? null} />;
  }

  const finding = findings[index];
  if (!finding) return null;

  const total = findings.length;
  const criticals = findings.filter((f) => f.status === "critical").length;
  const attentions = findings.filter((f) => f.status === "attention").length;
  const conforme = total - criticals - attentions;
  const hideSuggestions = context === "acervo";
  const classification = finding.metadata?.classification
    ? String(finding.metadata.classification)
    : classificationFromStatus(finding.status);

  const handleScroll = () => {
    if (!clauseBodyRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = clauseBodyRef.current;
    if (scrollHeight - scrollTop - clientHeight < 20) {
      setHasReadClause(true);
    }
  };

  const handleNext = () => {
    setIndex((i) => i + 1);
    setHasReadClause(false);
  };

  const handlePrevious = () => {
    setIndex((i) => Math.max(0, i - 1));
    setHasReadClause(false);
  };

  const handleDotClick = (dotIndex: number) => {
    setIndex(dotIndex);
    setHasReadClause(false);
  };

  return (
    <div className={styles.stepper}>
      <div className={styles.header}>
        <span className={styles.counter}>
          {criticals} críticos · {attentions} atenção · {conforme} conforme
        </span>
        <span className={styles.pagination}>
          Cláusula {index + 1} de {total}
        </span>
      </div>

      <div className={styles.clauseCard}>
        <div className={styles.clauseHeader}>
          <h3 className={styles.clauseTitle}>
            {CANONICAL_NAMES[finding.clauseName] || finding.clauseName}
          </h3>
          <span className={`${styles.classification} ${styles[`cls-${classification}`] || ""}`}>
            {classificationLabel(classification)}
          </span>
        </div>

        <div className={styles.clauseBody} ref={clauseBodyRef} onScroll={handleScroll}>
          <div className={styles.field}>
            <strong>Texto atual:</strong>
            <p>{finding.currentSummary}</p>
          </div>
          <div className={styles.field}>
            <strong>Regra da policy:</strong>
            <p>{finding.policyRule}</p>
          </div>
          {!hideSuggestions && (finding.status === "critical" || finding.status === "attention") && (
            <>
              <div className={styles.field}>
                <strong>Explicação do risco:</strong>
                <p className={styles.riskText}>{finding.riskExplanation}</p>
              </div>
              {finding.suggestedAdjustmentDirection && (
                <div className={styles.field}>
                  <strong>Direção sugerida:</strong>
                  <p className={styles.suggestionText}>{finding.suggestedAdjustmentDirection}</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <div className={styles.nav}>
        <button
          className={styles.navButton}
          disabled={index === 0}
          onClick={handlePrevious}
          type="button"
        >
          &larr; Anterior
        </button>
        <div className={styles.dots}>
          {findings.map((f, i) => (
            <button
              key={f.clauseName}
              className={`${styles.dot} ${i === index ? styles.dotActive : ""} ${styles[`dot-${f.status}`] || ""}`}
              onClick={() => handleDotClick(i)}
              type="button"
              aria-label={`Cláusula ${i + 1}: ${CANONICAL_NAMES[f.clauseName] || f.clauseName}`}
            />
          ))}
          <button
            className={`${styles.dot} ${styles.dotVerdict}`}
            onClick={() => { setIndex(findings.length); setHasReadClause(false); }}
            type="button"
            aria-label="Veredito final"
          >
            &#10003;
          </button>
        </div>
        <button
          className={styles.navButton}
          disabled={index === total - 1 && !hasReadClause}
          onClick={handleNext}
          type="button"
        >
          Próximo &rarr;
        </button>
      </div>
    </div>
  );
}