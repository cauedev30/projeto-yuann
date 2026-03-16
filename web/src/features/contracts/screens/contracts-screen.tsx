"use client";

import React from "react";
import { useState } from "react";

import {
  type ContractFinding,
  type ContractUploadInput,
  type ContractUploadResult,
} from "../../../entities/contracts/model";
import { uploadContract } from "../../../lib/api/contracts";
import { UploadForm } from "../components/upload-form";

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
    <main>
      <header>
        <p>Governanca contratual</p>
        <h1>Envie um contrato para triagem inicial</h1>
        <p>Suba um PDF para revisar a sessao atual e a triagem inicial do contrato.</p>
      </header>

      <UploadForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />

      <section aria-live="polite">
        <h2>Estado da sessao</h2>
        <p>{statusMessage}</p>
      </section>

      {error ? <p role="alert">{error}</p> : null}

      {result ? (
        <>
          <section>
            <h2>Resumo da triagem</h2>
            <p>Tipo enviado: {result.source}</p>
            <p>Status geral: {findings.some((item) => item.status === "critical") ? "Atencao" : "Conforme"}</p>
            <p>Score de risco: {riskScore}</p>
            <p>OCR utilizado: {result.usedOcr ? "sim" : "nao"}.</p>
          </section>

          <section>
            <h2>Findings principais</h2>
            <ul>
              {findings.map((item) => (
                <li key={`${item.clauseName}-${item.status}`}>
                  <strong>{item.clauseName}</strong>: {item.status} - {item.riskExplanation}
                </li>
              ))}
            </ul>
          </section>
          <section>
            <h2>Texto extraido</h2>
            <pre>{result.text}</pre>
          </section>
        </>
      ) : (
        <p>Envie um PDF para liberar o resumo da triagem, os findings e o texto extraido.</p>
      )}
    </main>
  );
}
