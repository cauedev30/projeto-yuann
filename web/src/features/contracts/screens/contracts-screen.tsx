"use client";

import React from "react";
import { useState } from "react";

import {
  type ContractFinding,
  type ContractUploadInput,
  type ContractUploadResult,
} from "../../../entities/contracts/model";
import { uploadContract } from "../../../lib/api/contracts";
import { ContractsHero } from "../components/contracts-hero";
import { ExtractedTextPanel } from "../components/extracted-text-panel";
import { FindingsSection } from "../components/findings-section";
import { SessionStatusCard } from "../components/session-status-card";
import { UploadSummaryCards } from "../components/upload-summary-cards";
import { UploadForm } from "../components/upload-form";
import styles from "./contracts-screen.module.css";

type ContractsScreenProps = {
  submitContract?: (payload: ContractUploadInput) => Promise<ContractUploadResult>;
};

function buildPreviewFindings(text: string): ContractFinding[] {
  const termMatch = text.match(/(\d+)\s*meses/i);
  const termMonths = termMatch ? Number(termMatch[1]) : null;

  if (termMonths !== null && termMonths < 60) {
    return [
      {
        clauseName: "Prazo de vigencia",
        status: "critical",
        riskExplanation: "Prazo abaixo do minimo permitido pela politica.",
        currentSummary: `Prazo atual de ${termMonths} meses.`,
        policyRule: "Prazo minimo exigido: 60 meses.",
        suggestedAdjustmentDirection: "Solicitar prazo minimo de 60 meses.",
      },
    ];
  }

  return [
    {
      clauseName: "Analise inicial",
      status: "conforme",
      riskExplanation: "Nenhum desvio critico identificado na triagem inicial.",
      currentSummary: "Texto extraido com sucesso.",
      policyRule: "Continuar com a analise juridica completa.",
      suggestedAdjustmentDirection: "Validar findings detalhados na proxima etapa.",
    },
  ];
}

export function ContractsScreen({
  submitContract = uploadContract,
}: ContractsScreenProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<ContractUploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const findings = result ? buildPreviewFindings(result.text) : [];
  const riskScore = findings.some((item) => item.status === "critical") ? 80 : 10;
  const statusState = error
    ? "error"
    : isSubmitting
      ? "loading"
      : result
        ? "success"
        : "empty";

  let statusMessage = "Nenhuma triagem foi executada nesta sessao.";

  if (statusState === "loading") {
    statusMessage = "Processando triagem inicial...";
  } else if (statusState === "error") {
    statusMessage = "Falha ao concluir a triagem inicial.";
  } else if (statusState === "success") {
    statusMessage = "Triagem inicial concluida";
  }

  async function handleSubmit(payload: ContractUploadInput) {
    setIsSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const response = await submitContract(payload);
      setResult(response);
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "Nao foi possivel concluir o envio.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className={styles.page}>
      <ContractsHero />

      <div className={styles.topGrid}>
        <section className={`${styles.panel} ${styles.uploadPanel}`}>
          <div className={styles.sectionHeader}>
            <div>
              <p className={styles.panelEyebrow}>Entrada principal</p>
              <h2 className={styles.sectionTitle}>Upload do contrato</h2>
            </div>
          </div>

          <p className={styles.panelDescription}>
            Escolha o tipo do documento e envie o PDF para iniciar a leitura automatizada da sessao.
          </p>

          <div className={styles.uploadShell}>
            <div className={styles.uploadHint}>
              <strong>Fluxo guiado</strong>
              <p>
                O retorno desta tela prioriza status da sessao, resumo executivo e findings antes do texto completo.
              </p>
            </div>

            <UploadForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />
          </div>
        </section>

        <SessionStatusCard
          state={statusState}
          message={statusState === "error" && error ? error : statusMessage}
        />
      </div>

      {result ? (
        <>
          <UploadSummaryCards
            hasCriticalFinding={findings.some((item) => item.status === "critical")}
            riskScore={riskScore}
            source={result.source}
            usedOcr={result.usedOcr}
          />
          <FindingsSection items={findings} />
          <ExtractedTextPanel text={result.text} />
        </>
      ) : (
        <section className={`${styles.panel} ${styles.emptyPanel}`}>
          <div className={styles.sectionHeader}>
            <div>
              <p className={styles.panelEyebrow}>Resultado</p>
              <h2 className={styles.sectionTitle}>A triagem aparece aqui</h2>
            </div>
            <span className={styles.emptyCallout}>Pronto para revisar</span>
          </div>

          <p className={styles.emptyCopy}>
            Envie um PDF para liberar o resumo da triagem, os findings e o texto extraido.
          </p>
        </section>
      )}
    </main>
  );
}
