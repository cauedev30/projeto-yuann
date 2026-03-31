"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React from "react";
import { useCallback, useEffect, useState } from "react";

import {
  type ContractFinding,
  type ContractListItemSummary,
  type ContractListResponse,
  type ContractUploadInput,
  type ContractUploadResult,
} from "../../../entities/contracts/model";
import { listContracts, uploadContract } from "../../../lib/api/contracts";
import { ContractsHero } from "../components/contracts-hero";
import { ContractSummaryPanel } from "../components/contract-summary-panel";
import { ContractsListPanel } from "../components/contracts-list-panel";
import { SessionStatusCard } from "../components/session-status-card";
import { UploadSummaryCards } from "../components/upload-summary-cards";
import { UploadForm } from "../components/upload-form";
import uiStyles from "../../../components/ui/ui-primitives.module.css";
import styles from "./contracts-screen.module.css";

type ContractsScreenProps = {
  submitContract?: (payload: ContractUploadInput) => Promise<ContractUploadResult>;
  loadContracts?: () => Promise<ContractListResponse>;
  navigateToContract?: (contractId: string) => void;
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
      currentSummary: "Resumo gerado com sucesso.",
      policyRule: "Continuar com a analise juridica completa.",
      suggestedAdjustmentDirection: "Validar os achados detalhados na proxima etapa.",
    },
  ];
}

function extractTermMonths(text: string): number | null {
  const termMatch = text.match(/(\d+)\s*meses/i);
  return termMatch ? Number(termMatch[1]) : null;
}

function buildUploadedContractListItem(
  payload: Pick<ContractUploadInput, "title" | "externalReference" | "source">,
  result: ContractUploadResult,
  findings: ContractFinding[],
): ContractListItemSummary {
  const hasCriticalFinding = findings.some((item) => item.status === "critical");

  return {
    id: result.contractId,
    title: payload.title,
    externalReference: payload.externalReference,
    status: hasCriticalFinding ? "revisao_prioritaria" : "analisado",
    signatureDate: null,
    startDate: null,
    endDate: null,
    termMonths: extractTermMonths(result.text),
    isActive: false,
    activatedAt: null,
    lastAccessedAt: null,
    lastAnalyzedAt: null,
    latestAnalysisStatus: "completed",
    latestRiskScore: null,
    latestVersionSource: result.source,
  };
}

export function ContractsScreen({
  submitContract = uploadContract,
  loadContracts = listContracts,
  navigateToContract,
}: ContractsScreenProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<ContractUploadResult | null>(null);
  const [submittedContract, setSubmittedContract] = useState<
    Pick<ContractUploadInput, "title" | "externalReference" | "source"> | null
  >(null);
  const [error, setError] = useState<string | null>(null);
  const [contracts, setContracts] = useState<ContractListResponse["items"]>([]);
  const [isLoadingContracts, setIsLoadingContracts] = useState(true);
  const [isRefreshingContracts, setIsRefreshingContracts] = useState(false);
  const [contractsError, setContractsError] = useState<string | null>(null);

  const [showSuccessBanner, setShowSuccessBanner] = useState(false);

  const findings = result ? buildPreviewFindings(result.text) : [];
  const uploadedContract =
    result && submittedContract
      ? buildUploadedContractListItem(submittedContract, result, findings)
      : null;

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

  useEffect(() => {
    if (!showSuccessBanner) return;
    const timer = setTimeout(() => setShowSuccessBanner(false), 5000);
    return () => clearTimeout(timer);
  }, [showSuccessBanner]);

  useEffect(() => {
    let isActive = true;

    async function loadPersistedContracts() {
      setIsLoadingContracts(true);
      setContractsError(null);

      try {
        const response = await loadContracts();
        if (!isActive) {
          return;
        }

        setContracts(response.items);
      } catch (loadError) {
        if (!isActive) {
          return;
        }

        setContractsError(
          loadError instanceof Error
            ? loadError.message
            : "Nao foi possivel carregar os contratos.",
        );
      } finally {
        if (isActive) {
          setIsLoadingContracts(false);
        }
      }
    }

    void loadPersistedContracts();

    return () => {
      isActive = false;
    };
  }, [loadContracts]);

  const refreshPersistedContracts = useCallback(async () => {
    setIsRefreshingContracts(true);
    setContractsError(null);

    try {
      const response = await loadContracts();
      setContracts(response.items);
    } catch (refreshError) {
      setContractsError(
        refreshError instanceof Error
          ? refreshError.message
          : "Nao foi possivel carregar os contratos.",
      );
    } finally {
      setIsRefreshingContracts(false);
    }
  }, [loadContracts]);

  async function handleSubmit(payload: ContractUploadInput) {
    setIsSubmitting(true);
    setError(null);
    setResult(null);
    setSubmittedContract(null);
    try {
      const response = await submitContract(payload);
      setSubmittedContract({
        title: payload.title,
        externalReference: payload.externalReference,
        source: payload.source,
      });
      setResult(response);
      setShowSuccessBanner(true);
      await refreshPersistedContracts();
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
      <div aria-atomic="true" aria-live="polite" className="sr-only">
        {isSubmitting ? "Processando triagem inicial..." : ""}
        {isLoadingContracts ? "Carregando contratos..." : ""}
        {isRefreshingContracts ? "Atualizando contratos..." : ""}
        {!isLoadingContracts && !contractsError ? `${contracts.length} contratos sincronizados.` : ""}
        {error ?? contractsError ?? ""}
      </div>

      {showSuccessBanner && (
        <div className={styles.successBanner} role="status">
          Triagem concluida com sucesso — contrato adicionado ao acervo.
        </div>
      )}

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
            Escolha a origem do documento e envie o PDF para abrir a leitura inicial do
            contrato com a mesa juridica da sessao.
          </p>

          <div className={styles.uploadShell}>
            <div className={styles.uploadHint}>
              <strong>Leitura guiada</strong>
              <p>
                O retorno desta tela prioriza status da sessao, resumo executivo e
                achados antes do texto integral.
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
            source={result.source}
            usedOcr={result.usedOcr}
          />
          {uploadedContract ? (
            <ContractsListPanel
              items={[uploadedContract]}
              isLoading={false}
              isRefreshing={false}
              error={null}
              onRefresh={() => undefined}
              eyebrow="Análise pronta"
              title="Contrato analisado"
              navigateToContract={(contractId) =>
                navigateToContract
                  ? navigateToContract(contractId)
                  : router.push(`/contracts/${contractId}`)
              }
            />
          ) : null}
          <ContractSummaryPanel contractId={result.contractId} />
        </>
      ) : (
        <section className={`${styles.panel} ${styles.emptyPanel}`}>
          <div className={styles.sectionHeader}>
            <div>
              <p className={styles.panelEyebrow}>Resultado</p>
              <h2 className={styles.sectionTitle}>A leitura aparece aqui</h2>
            </div>
            <span className={styles.emptyCallout}>Mesa pronta</span>
          </div>

          <p className={styles.emptyCopy}>
            Envie um PDF para liberar o resumo da triagem, os achados e o resumo em inteligência artificial.
          </p>
        </section>
      )}

      <section className={`${styles.panel} ${styles.emptyPanel}`}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.panelEyebrow}>Navegação</p>
            <h2 className={styles.sectionTitle}>Acessar Acervo</h2>
          </div>
        </div>
        <p className={styles.emptyCopy}>
          Contratos ativos e o histórico operacional foram movidos para rotas dedicadas.
        </p>
        <div className={styles.navActions}>
          <Link
            href="/acervo"
            className={`${uiStyles.buttonPrimary} ${styles.navLink}`}
          >
            Abrir Acervo
          </Link>
          <Link
            href="/historico"
            className={`${uiStyles.buttonSecondary} ${styles.navLink}`}
          >
            Abrir Histórico
          </Link>
        </div>
      </section>
    </main>
  );
}
