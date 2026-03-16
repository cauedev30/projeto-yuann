"use client";

import React from "react";
import { useState } from "react";

import {
  type ContractFinding,
  type ContractUploadInput,
  type ContractUploadResult,
} from "../../../entities/contracts/model";
import { uploadContract } from "../../../lib/api/contracts";
import { FindingsTable } from "../../analysis/components/findings-table";
import { RiskScoreCard } from "../../analysis/components/risk-score-card";
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

  async function handleSubmit(payload: ContractUploadInput) {
    setIsSubmitting(true);
    setError(null);
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
        <p>Governanca de contratos de expansao</p>
        <h1>Contratos recebidos</h1>
      </header>

      <UploadForm onSubmit={handleSubmit} isSubmitting={isSubmitting} />

      {error ? <p role="alert">{error}</p> : null}

      {result ? (
        <section>
          <RiskScoreCard
            score={riskScore}
            summary={`OCR utilizado: ${result.usedOcr ? "sim" : "nao"}.`}
          />
          <FindingsTable items={findings} />
          <pre>{result.text}</pre>
        </section>
      ) : (
        <p>Nenhum contrato enviado nesta sessao.</p>
      )}
    </main>
  );
}
