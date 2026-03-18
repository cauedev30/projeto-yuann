"use client";

import React from "react";
import { useEffect, useState } from "react";

import { EmptyState } from "../../../components/ui/empty-state";
import { LoadingSkeleton } from "../../../components/ui/loading-skeleton";
import { PageHeader } from "../../../components/ui/page-header";
import { StatCard } from "../../../components/ui/stat-card";
import { SurfaceCard } from "../../../components/ui/surface-card";
import type { ContractDetail } from "../../../entities/contracts/model";
import { ContractsApiError, getContractDetail } from "../../../lib/api/contracts";
import { EventTimeline } from "../components/event-timeline";
import { ExtractedTextPanel } from "../components/extracted-text-panel";
import { FindingsSection } from "../components/findings-section";
import { MetadataSection } from "../components/metadata-section";
import styles from "./contract-detail-screen.module.css";

type ContractDetailScreenProps = {
  contractId: string;
  loadContractDetail?: (contractId: string) => Promise<ContractDetail>;
};

function buildContractDescription(detail: ContractDetail): string {
  return `Referencia ${detail.contract.externalReference} com leitura persistida, versao mais recente e analise canonica.`;
}

function isNotFoundError(error: unknown): error is ContractsApiError {
  return error instanceof ContractsApiError && error.statusCode === 404;
}

function normalizeDetailError(detailError: unknown): Error {
  return detailError instanceof Error
    ? detailError
    : new Error("Nao foi possivel carregar o contrato.");
}

export function ContractDetailScreen({
  contractId,
  loadContractDetail = getContractDetail,
}: ContractDetailScreenProps) {
  const [detail, setDetail] = useState<ContractDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const liveMessage = isRefreshing
    ? "Atualizando detalhe do contrato..."
    : isLoading
      ? "Carregando contrato..."
      : error?.message ?? "";

  useEffect(() => {
    let isActive = true;

    async function load() {
      setIsLoading(true);
      setError(null);

      try {
        const response = await loadContractDetail(contractId);
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
  }, [contractId, loadContractDetail]);

  async function handleRefresh() {
    setIsRefreshing(true);
    setError(null);

    try {
      const response = await loadContractDetail(contractId);
      setDetail(response);
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
      const response = await loadContractDetail(contractId);
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
          eyebrow="Contracts"
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
          eyebrow="Contracts"
          title="Contrato nao encontrado."
          description="O identificador informado nao corresponde a um contrato persistido no backend."
        />
        <EmptyState
          body="Revise a navegacao da lista e tente abrir o contrato novamente."
          title="Contrato nao encontrado."
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
          eyebrow="Contracts"
          title={contractId}
          description="Falha ao carregar a leitura completa deste contrato."
        />
        <SurfaceCard title="Detalhe do contrato">
          <div className={styles.stack}>
            <p className={styles.alert} role="alert">
              {error?.message ?? "Nao foi possivel carregar o contrato."}
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

  return (
    <section className={styles.page}>
      <div aria-atomic="true" aria-live="polite" className="sr-only">
        {liveMessage}
      </div>
      <PageHeader
        eyebrow="Contracts"
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
        <div className={styles.statGrid}>
          <StatCard label="Status" value={detail.contract.status} />
          <StatCard
            label="Prazo"
            value={
              detail.contract.termMonths !== null
                ? `${detail.contract.termMonths} meses`
                : "a confirmar"
            }
          />
          <StatCard
            label="Score"
            value={detail.latestAnalysis?.contractRiskScore ?? "a confirmar"}
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

          <SurfaceCard title="Ultima versao">
            {detail.latestVersion ? (
              <dl className={styles.summaryList}>
                <div className={styles.summaryRow}>
                  <dt>Arquivo</dt>
                  <dd>{detail.latestVersion.originalFilename}</dd>
                </div>
                <div className={styles.summaryRow}>
                  <dt>Origem</dt>
                  <dd>{detail.latestVersion.source}</dd>
                </div>
                <div className={styles.summaryRow}>
                  <dt>Processamento</dt>
                  <dd>{detail.latestVersion.usedOcr ? "OCR" : "Texto direto"}</dd>
                </div>
              </dl>
            ) : (
              <p className={styles.inlineText}>Versao ainda nao disponivel.</p>
            )}
          </SurfaceCard>
        </div>

        <EventTimeline events={detail.events} />

        <SurfaceCard title="Ultima analise">
          {detail.latestAnalysis ? (
            <div className={styles.stack}>
              <p className={styles.inlineText}>
                Politica {detail.latestAnalysis.policyVersion} com status{" "}
                {detail.latestAnalysis.analysisStatus}.
              </p>
              <FindingsSection items={detail.latestAnalysis.findings} />
            </div>
          ) : (
            <p className={styles.inlineText}>Analise ainda nao disponivel.</p>
          )}
        </SurfaceCard>

        {detail.latestVersion?.text ? (
          <ExtractedTextPanel text={detail.latestVersion.text} />
        ) : null}
      </div>
    </section>
  );
}
