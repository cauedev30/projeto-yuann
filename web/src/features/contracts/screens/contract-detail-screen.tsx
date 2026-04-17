"use client";

import Link from "next/link";
import React from "react";
import { useCallback, useEffect, useState } from "react";

import { EmptyState } from "../../../components/ui/empty-state";
import { LoadingSkeleton } from "../../../components/ui/loading-skeleton";
import { PageHeader } from "../../../components/ui/page-header";
import { StatCard } from "../../../components/ui/stat-card";
import { SurfaceCard } from "../../../components/ui/surface-card";
import type { ContractDetail } from "../../../entities/contracts/model";
import {
  ContractsApiError,
  getContractDetail,
  getContractVersionDetail,
  getDownloadCorrectedUrl,
} from "../../../lib/api/contracts";
import { useGenerateCorrectedContract } from "../../../lib/hooks/use-contracts";
import { ContractSummaryPanel } from "../components/contract-summary-panel";
import { ClauseStepper } from "../components/clause-stepper";
import { EventTimeline } from "../components/event-timeline";
import { ExtractedTextPanel } from "../components/extracted-text-panel";
import { FindingsSection } from "../components/findings-section";
import { MetadataSection } from "../components/metadata-section";
import styles from "./contract-detail-screen.module.css";

const SOURCE_LABELS: Record<string, string> = {
  third_party_draft: "Contrato padrão",
  signed_contract: "Contrato assinado",
};

const CONTRACT_STATUS_LABELS: Record<string, string> = {
  uploaded: "Enviado",
  analyzed: "Analisado",
  active: "Ativo",
  archived: "Arquivado",
};

type ContractDetailScreenProps = {
  contractId: string;
  versionId?: string | null;
  context?: "acervo" | "historico" | "contracts";
  loadContractDetail?: (contractId: string) => Promise<ContractDetail>;
  loadContractVersionDetail?: (contractId: string, versionId: string) => Promise<ContractDetail>;
};

function buildContractDescription(detail: ContractDetail): string {
  if (detail.isHistoricalView && detail.selectedVersion && detail.latestVersion) {
    return `Referência ${detail.contract.externalReference} em leitura histórica da versão ${detail.selectedVersion.versionNumber}. A versão atual é a ${detail.latestVersion.versionNumber}.`;
  }

  return `Referência ${detail.contract.externalReference} com leitura da versão atual do contrato.`;
}

function isNotFoundError(error: unknown): error is ContractsApiError {
  return error instanceof ContractsApiError && error.statusCode === 404;
}

function normalizeDetailError(detailError: unknown): Error {
  return detailError instanceof Error
    ? detailError
    : new Error("Não foi possível carregar o contrato.");
}

function formatSelectedVersionTimestamp(detail: ContractDetail): string {
  if (!detail.selectedVersion) {
    return "";
  }

  const timestamp = new Date(detail.selectedVersion.createdAt);
  if (Number.isNaN(timestamp.getTime())) {
    return detail.selectedVersion.createdAt;
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(timestamp);
}

function formatContractStatus(status: string): string {
  return CONTRACT_STATUS_LABELS[status] ?? status;
}

export function ContractDetailScreen({
  contractId,
  versionId,
  context = "contracts",
  loadContractDetail = getContractDetail,
  loadContractVersionDetail = getContractVersionDetail,
}: ContractDetailScreenProps) {
  const [detail, setDetail] = useState<ContractDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [correctedReady, setCorrectedReady] = useState(false);

  const generateCorrected = useGenerateCorrectedContract();

  const liveMessage = isLoading ? "Carregando contrato..." : error?.message ?? "";

  useEffect(() => {
    setCorrectedReady(false);
  }, [contractId, versionId]);

  const loadCurrentSelection = useCallback(async () => (
    versionId
      ? loadContractVersionDetail(contractId, versionId)
      : loadContractDetail(contractId)
  ), [contractId, loadContractDetail, loadContractVersionDetail, versionId]);

  useEffect(() => {
    let isActive = true;

    async function load() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await loadCurrentSelection();
        if (!isActive) {
          return;
        }

        setDetail(response);
      } catch (detailError) {
        if (!isActive) {
          return;
        }

        setDetail(null);
        setError(normalizeDetailError(detailError));
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    void load();

    return () => {
      isActive = false;
    };
  }, [loadCurrentSelection]);

  async function handleRetry() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await loadCurrentSelection();
      setDetail(response);
    } catch (detailError) {
      setDetail(null);
      setError(normalizeDetailError(detailError));
    } finally {
      setIsLoading(false);
    }
  }

  if (isLoading) {
    return (
      <section className={styles.page}>
        <div aria-atomic="true" aria-live="polite" className="sr-only">
          {liveMessage}
        </div>
        <PageHeader
          eyebrow="Contratos"
          title={contractId}
          description="Carregando a leitura persistida deste contrato."
        />
        <SurfaceCard title="Detalhe do contrato">
          <LoadingSkeleton heading lines={4} />
        </SurfaceCard>
      </section>
    );
  }

  if (error && isNotFoundError(error)) {
    return (
      <section className={styles.page}>
        <div aria-atomic="true" aria-live="polite" className="sr-only">
          {liveMessage}
        </div>
        <PageHeader
          eyebrow="Contratos"
          title="Contrato não encontrado."
          description="O identificador informado não corresponde a um contrato persistido no backend."
        />
        <EmptyState
          body="Revise a navegação da lista e tente abrir o contrato novamente."
          title="Contrato não encontrado."
        />
      </section>
    );
  }

  if (error || !detail) {
    return (
      <section className={styles.page}>
        <div aria-atomic="true" aria-live="polite" className="sr-only">
          {liveMessage}
        </div>
        <PageHeader
          eyebrow="Contratos"
          title={contractId}
          description="Falha ao carregar a leitura completa deste contrato."
        />
        <SurfaceCard title="Detalhe do contrato">
          <div className={styles.stack}>
            <p className={styles.alert} role="alert">
              {error?.message ?? "Não foi possível carregar o contrato."}
            </p>
            <div className={styles.refreshRow}>
              <button
                className={styles.refreshButton}
                onClick={() => void handleRetry()}
                type="button"
              >
                Tentar novamente
              </button>
            </div>
          </div>
        </SurfaceCard>
      </section>
    );
  }

  const selectedVersion = detail.selectedVersion;
  const selectedAnalysis = detail.selectedAnalysis;

  return (
    <section className={styles.page}>
      <div aria-atomic="true" aria-live="polite" className="sr-only">
        {liveMessage}
      </div>
      <nav aria-label="Breadcrumb" className={styles.breadcrumb}>
        <Link href="/contracts" className={styles.breadcrumbLink}>Contratos</Link>
        <span aria-hidden="true" className={styles.breadcrumbSeparator}>/</span>
        <span className={styles.breadcrumbCurrent}>{detail.contract.title}</span>
      </nav>
      <PageHeader
        eyebrow="Contratos"
        title={detail.contract.title}
        description={buildContractDescription(detail)}
      />

      <div className={styles.stack}>
        {detail.isHistoricalView && detail.selectedVersion && detail.latestVersion ? (
          <SurfaceCard title="Versão histórica">
            <p className={styles.inlineText}>
              Você está vendo a versão {detail.selectedVersion.versionNumber}. A atual é a versão{" "}
              {detail.latestVersion.versionNumber}.
            </p>
          </SurfaceCard>
        ) : null}

        <div className={styles.statGrid}>
          <StatCard compact label="Status" value={formatContractStatus(detail.contract.status)} />
          <StatCard
            compact
            label="Prazo"
            value={
              detail.contract.termMonths !== null
                ? `${detail.contract.termMonths} meses`
                : "a confirmar"
            }
          />
        </div>

        <div className={styles.detailGrid}>
          <MetadataSection
            parties={detail.contract.parties}
            financialTerms={detail.contract.financialTerms}
            fieldConfidence={detail.contract.fieldConfidence}
            signatureDate={detail.contract.signatureDate}
            startDate={detail.contract.startDate}
            endDate={detail.contract.endDate}
          />

          <SurfaceCard title="Versão em visualização">
            {selectedVersion ? (
              <dl className={styles.summaryList}>
                <div className={styles.summaryRow}>
                  <dt>Versão</dt>
                  <dd>{selectedVersion.versionNumber}</dd>
                </div>
                <div className={styles.summaryRow}>
                  <dt>Arquivo</dt>
                  <dd>{selectedVersion.originalFilename}</dd>
                </div>
                <div className={styles.summaryRow}>
                  <dt>Origem</dt>
                  <dd>{SOURCE_LABELS[selectedVersion.source] ?? selectedVersion.source}</dd>
                </div>
                <div className={styles.summaryRow}>
                  <dt>Processamento</dt>
                  <dd>{selectedVersion.usedOcr ? "OCR" : "Texto direto"}</dd>
                </div>
                <div className={styles.summaryRow}>
                  <dt>Registrada em</dt>
                  <dd>{formatSelectedVersionTimestamp(detail)}</dd>
                </div>
              </dl>
            ) : (
              <p className={styles.inlineText}>Versão ainda não disponível.</p>
            )}
          </SurfaceCard>
        </div>

        {selectedAnalysis && selectedAnalysis.findings.length > 0 && (
          <SurfaceCard title="Análise de Cláusulas">
            <ClauseStepper
              findings={selectedAnalysis.findings}
              context={context}
              riskScore={selectedAnalysis.contractRiskScore}
            />
          </SurfaceCard>
        )}

        <details className={styles.collapsible} open>
          <summary className={styles.collapsibleSummary}>
            <span className={styles.collapsibleTitle}>Timeline de eventos</span>
            <span className={styles.collapsibleChevron} aria-hidden="true" />
          </summary>
          <div className={styles.collapsibleContent}>
            <EventTimeline events={detail.events} />
          </div>
        </details>

        <details className={styles.collapsible} open>
          <summary className={styles.collapsibleSummary}>
            <span className={styles.collapsibleTitle}>Análise da versão</span>
            <span className={styles.collapsibleChevron} aria-hidden="true" />
          </summary>
          <div className={styles.collapsibleContent}>
            {selectedAnalysis ? (
              <div className={styles.stack}>
                <FindingsSection items={selectedAnalysis.findings} />

                {!detail.isHistoricalView && selectedAnalysis.analysisStatus === "completed" ? (
                  <div className={styles.actionRow}>
                    {!correctedReady ? (
                      <button
                        className={styles.primaryButton}
                        onClick={async () => {
                          try {
                            await generateCorrected.mutateAsync(contractId);
                            setCorrectedReady(true);
                          } catch {
                            // error handled by mutation state
                          }
                        }}
                        disabled={generateCorrected.isPending}
                        type="button"
                      >
                        {generateCorrected.isPending
                          ? "Gerando contrato corrigido..."
                          : "Gerar Contrato Corrigido"}
                      </button>
                    ) : (
                      <a
                        className={styles.primaryButton}
                        href={getDownloadCorrectedUrl(contractId)}
                        download
                      >
                        Baixar Contrato Corrigido (.docx)
                      </a>
                    )}
                    {generateCorrected.isError ? (
                      <p className={styles.errorText}>
                        Erro ao gerar: {generateCorrected.error?.message}
                      </p>
                    ) : null}
                  </div>
                ) : null}
              </div>
            ) : (
              <p className={styles.inlineText}>Análise ainda não disponível.</p>
            )}
          </div>
        </details>

        <details className={styles.collapsible} open>
          <summary className={styles.collapsibleSummary}>
            <span className={styles.collapsibleTitle}>Resumo do contrato</span>
            <span className={styles.collapsibleChevron} aria-hidden="true" />
          </summary>
          <div className={styles.collapsibleContent}>
            <ContractSummaryPanel contractId={contractId} versionId={versionId} />
          </div>
        </details>

        {selectedVersion?.text ? (
          <details className={styles.collapsible}>
            <summary className={styles.collapsibleSummary}>
              <span className={styles.collapsibleTitle}>Texto extraído</span>
              <span className={styles.collapsibleChevron} aria-hidden="true" />
            </summary>
            <div className={styles.collapsibleContent}>
              <ExtractedTextPanel text={selectedVersion.text} />
            </div>
          </details>
        ) : null}
      </div>
    </section>
  );
}
