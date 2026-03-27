"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React from "react";
import { useEffect, useState } from "react";

import { EmptyState } from "../../../components/ui/empty-state";
import { LoadingSkeleton } from "../../../components/ui/loading-skeleton";
import { PageHeader } from "../../../components/ui/page-header";
import { StatCard } from "../../../components/ui/stat-card";
import { SurfaceCard } from "../../../components/ui/surface-card";
import type { ContractDetail } from "../../../entities/contracts/model";
import {
  compareContractVersions,
  ContractsApiError,
  getContractDetail,
  listContractVersions,
  getContractVersionDetail,
  getDownloadCorrectedUrl,
} from "../../../lib/api/contracts";
import { useGenerateCorrectedContract } from "../../../lib/hooks/use-contracts";
import { ContractSummaryPanel } from "../components/contract-summary-panel";
import { EventTimeline } from "../components/event-timeline";
import { ExtractedTextPanel } from "../components/extracted-text-panel";
import { FindingsSection } from "../components/findings-section";
import { MetadataSection } from "../components/metadata-section";
import { VersionDiffPanel } from "../components/version-diff-panel";
import { VersionHistoryPanel } from "../components/version-history-panel";
import styles from "./contract-detail-screen.module.css";

const SOURCE_LABELS: Record<string, string> = {
  third_party_draft: "Minuta de terceiro",
  signed_contract: "Contrato assinado",
};

const CONTRACT_STATUS_LABELS: Record<string, string> = {
  uploaded: "Enviado",
  analyzed: "Analisado",
  active: "Ativo",
  archived: "Arquivado",
};

const ANALYSIS_STATUS_LABELS: Record<string, string> = {
  completed: "concluída",
  pending: "pendente",
  failed: "com falha",
};

type ContractDetailScreenProps = {
  contractId: string;
  versionId?: string | null;
  loadContractDetail?: (contractId: string) => Promise<ContractDetail>;
  loadContractVersionDetail?: (contractId: string, versionId: string) => Promise<ContractDetail>;
  loadContractVersions?: typeof listContractVersions;
  compareVersions?: typeof compareContractVersions;
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

function formatAnalysisStatus(status: string): string {
  return ANALYSIS_STATUS_LABELS[status] ?? status;
}

function getSelectedVersionId(detail: ContractDetail | null): string | null {
  if (!detail) {
    return null;
  }

  return detail.selectedVersion?.contractVersionId ?? detail.latestVersion?.contractVersionId ?? null;
}

function getDefaultBaselineId(
  versions: Awaited<ReturnType<typeof listContractVersions>>["items"],
  selectedVersionId: string | null,
): string | null {
  if (!selectedVersionId) {
    return null;
  }

  const selectedIndex = versions.findIndex((item) => item.contractVersionId === selectedVersionId);
  if (selectedIndex === -1) {
    return versions.find((item) => item.contractVersionId !== selectedVersionId)?.contractVersionId ?? null;
  }
  if (selectedIndex + 1 < versions.length) {
    return versions[selectedIndex + 1]?.contractVersionId ?? null;
  }
  if (selectedIndex > 0) {
    return versions[selectedIndex - 1]?.contractVersionId ?? null;
  }
  return null;
}

export function ContractDetailScreen({
  contractId,
  versionId,
  loadContractDetail = getContractDetail,
  loadContractVersionDetail = getContractVersionDetail,
  loadContractVersions = listContractVersions,
  compareVersions = compareContractVersions,
}: ContractDetailScreenProps) {
  const router = useRouter();
  const [detail, setDetail] = useState<ContractDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshSuccess, setRefreshSuccess] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [correctedReady, setCorrectedReady] = useState(false);
  const [versions, setVersions] = useState<Awaited<ReturnType<typeof listContractVersions>>["items"]>([]);
  const [isLoadingVersions, setIsLoadingVersions] = useState(true);
  const [versionsError, setVersionsError] = useState<string | null>(null);
  const [comparisonBaselineId, setComparisonBaselineId] = useState<string | null>(null);
  const [comparison, setComparison] = useState<Awaited<ReturnType<typeof compareContractVersions>> | null>(null);
  const [isLoadingComparison, setIsLoadingComparison] = useState(false);
  const [comparisonError, setComparisonError] = useState<string | null>(null);

  const generateCorrected = useGenerateCorrectedContract();

  const liveMessage = isRefreshing
    ? "Atualizando detalhe do contrato..."
    : isLoading
      ? "Carregando contrato..."
      : error?.message ?? "";

  useEffect(() => {
    if (!refreshSuccess) return;
    const timer = setTimeout(() => setRefreshSuccess(false), 2000);
    return () => clearTimeout(timer);
  }, [refreshSuccess]);

  useEffect(() => {
    setCorrectedReady(false);
  }, [contractId, versionId]);

  useEffect(() => {
    setComparisonBaselineId(null);
  }, [contractId, versionId]);

  useEffect(() => {
    let isActive = true;

    async function load() {
      setIsLoading(true);
      setError(null);

      try {
        const response = versionId
          ? await loadContractVersionDetail(contractId, versionId)
          : await loadContractDetail(contractId);
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
  }, [contractId, versionId, loadContractDetail, loadContractVersionDetail]);

  useEffect(() => {
    let isActive = true;

    async function loadVersions() {
      setIsLoadingVersions(true);
      setVersionsError(null);

      try {
        const response = await loadContractVersions(contractId);
        if (!isActive) {
          return;
        }

        setVersions(response.items);
      } catch (loadVersionsError) {
        if (!isActive) {
          return;
        }

        setVersions([]);
        setVersionsError(
          loadVersionsError instanceof Error
            ? loadVersionsError.message
            : "Não foi possível carregar o histórico de versões.",
        );
      } finally {
        if (isActive) {
          setIsLoadingVersions(false);
        }
      }
    }

    void loadVersions();

    return () => {
      isActive = false;
    };
  }, [contractId, loadContractVersions]);

  const selectedVersionId = getSelectedVersionId(detail);
  const effectiveBaselineId =
    comparisonBaselineId && comparisonBaselineId !== selectedVersionId
      ? comparisonBaselineId
      : getDefaultBaselineId(versions, selectedVersionId);

  useEffect(() => {
    let isActive = true;

    async function loadComparison() {
      if (!selectedVersionId || !effectiveBaselineId) {
        setComparison(null);
        setComparisonError(null);
        setIsLoadingComparison(false);
        return;
      }

      setIsLoadingComparison(true);
      setComparisonError(null);

      try {
        const response = await compareVersions(contractId, {
          selectedVersionId,
          baselineVersionId: effectiveBaselineId,
        });
        if (!isActive) {
          return;
        }

        setComparison(response);
      } catch (loadComparisonError) {
        if (!isActive) {
          return;
        }

        setComparison(null);
        setComparisonError(
          loadComparisonError instanceof Error
            ? loadComparisonError.message
            : "Não foi possível comparar as versões.",
        );
      } finally {
        if (isActive) {
          setIsLoadingComparison(false);
        }
      }
    }

    void loadComparison();

    return () => {
      isActive = false;
    };
  }, [compareVersions, contractId, effectiveBaselineId, selectedVersionId]);

  async function loadCurrentSelection() {
    return versionId
      ? loadContractVersionDetail(contractId, versionId)
      : loadContractDetail(contractId);
  }

  async function handleRefresh() {
    setIsRefreshing(true);
    setError(null);

    try {
      const response = await loadCurrentSelection();
      setDetail(response);
      setRefreshSuccess(true);
    } catch (detailError) {
      setDetail(null);
      setError(normalizeDetailError(detailError));
    } finally {
      setIsRefreshing(false);
    }
  }

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
  const currentVersionId = detail.latestVersion?.contractVersionId ?? null;

  function handleOpenVersion(nextVersionId: string | null) {
    if (!nextVersionId || nextVersionId === currentVersionId) {
      router.push(`/contracts/${contractId}`);
      return;
    }

    router.push(`/contracts/${contractId}?versionId=${nextVersionId}`);
  }

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

      <div className={styles.refreshRow}>
        <button
          className={styles.refreshButton}
          disabled={isRefreshing}
          onClick={() => void handleRefresh()}
          type="button"
        >
          {isRefreshing ? "Atualizando..." : "Atualizar detalhe"}
        </button>
      </div>

      <div className={styles.stack}>
        {refreshSuccess ? (
          <p className={styles.successText}>Detalhe atualizado.</p>
        ) : null}

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
          <StatCard
            compact
            label="Score"
            value={selectedAnalysis?.contractRiskScore ?? "a confirmar"}
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

        <div className={styles.detailGrid}>
          <VersionHistoryPanel
            versions={versions}
            isLoading={isLoadingVersions}
            errorMessage={versionsError}
            selectedVersionId={selectedVersionId}
            comparisonBaselineId={effectiveBaselineId}
            onOpenVersion={handleOpenVersion}
            onCompareWith={setComparisonBaselineId}
          />
          <VersionDiffPanel
            comparison={comparison}
            isLoading={isLoadingComparison}
            errorMessage={comparisonError}
          />
        </div>

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
                <p className={styles.inlineText}>
                  Política {selectedAnalysis.policyVersion} com status{" "}
                  {formatAnalysisStatus(selectedAnalysis.analysisStatus)}.
                </p>
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
