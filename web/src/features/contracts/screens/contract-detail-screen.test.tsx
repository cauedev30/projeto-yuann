import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ContractsApiError } from "../../../lib/api/contracts";
import { ContractDetailScreen } from "./contract-detail-screen";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

vi.mock("../../../lib/hooks/use-contracts", () => ({
  useGenerateCorrectedContract: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
    isError: false,
    error: null,
  }),
}));

vi.mock("../components/contract-summary-panel", () => ({
  ContractSummaryPanel: ({
    contractId,
    versionId,
  }: {
    contractId: string;
    versionId?: string | null;
  }) => <div>Resumo {contractId} {versionId ?? "current"}</div>,
}));

vi.mock("../components/event-timeline", () => ({
  EventTimeline: ({ events }: { events: Array<{ eventType: string }> }) => (
    <div>{events.length > 0 ? "Renovação" : "Nenhum evento identificado"}</div>
  ),
}));

vi.mock("../components/findings-section", () => ({
  FindingsSection: ({ items }: { items: Array<{ clauseName: string }> }) => (
    <div>{items.map((item) => item.clauseName).join(", ")}</div>
  ),
}));

vi.mock("../components/metadata-section", () => ({
  MetadataSection: () => <div>Metadados renderizados</div>,
}));

vi.mock("../components/extracted-text-panel", () => ({
  ExtractedTextPanel: ({ text }: { text: string }) => <div>{text}</div>,
}));

vi.mock("../components/version-history-panel", () => ({
  VersionHistoryPanel: ({
    versions,
    selectedVersionId,
    onOpenVersion,
    onCompareWith,
    comparisonBaselineId,
  }: {
    versions: Array<{ contractVersionId: string; versionNumber: number }>;
    selectedVersionId: string | null;
    comparisonBaselineId: string | null;
    onOpenVersion: (contractVersionId: string | null) => void;
    onCompareWith: (contractVersionId: string | null) => void;
  }) => (
    <div>
      <div>Histórico de versões</div>
      <div>Versoes carregadas: {versions.map((item) => item.versionNumber).join(", ")}</div>
      <div>Selecionada: {selectedVersionId ?? "current"}</div>
      <div>Base de comparação: {comparisonBaselineId ?? "none"}</div>
      <button onClick={() => onOpenVersion("ver-1")} type="button">
        Abrir versao 1
      </button>
      <button onClick={() => onCompareWith("ver-1")} type="button">
        Usar como base de comparação
      </button>
    </div>
  ),
}));

vi.mock("../components/version-diff-panel", () => ({
  VersionDiffPanel: ({
    comparison,
    isLoading,
  }: {
    comparison: { summary: string } | null;
    isLoading: boolean;
  }) => (
    <div>
      <div>Painel de comparação</div>
      <div>{isLoading ? "Carregando comparação..." : comparison?.summary ?? "Nenhuma comparação selecionada."}</div>
    </div>
  ),
}));

function buildContractDetail({
  isHistoricalView = false,
  correctedReady = false,
}: {
  isHistoricalView?: boolean;
  correctedReady?: boolean;
} = {}) {
  const selectedVersion = isHistoricalView
    ? {
        contractVersionId: "ver-1",
        versionNumber: 1,
        createdAt: "2026-03-20T12:00:00Z",
        source: "third_party_draft" as const,
        originalFilename: "contract-v1.pdf",
        usedOcr: false,
        text: "Texto da versao 1",
      }
    : {
        contractVersionId: "ver-2",
        versionNumber: 2,
        createdAt: "2026-03-21T12:00:00Z",
        source: "third_party_draft" as const,
        originalFilename: "contract-v2.pdf",
        usedOcr: false,
        text: "Texto da versao 2",
      };

  return {
    contract: {
      id: "ctr-1",
      title: "Loja Centro",
      externalReference: "LOC-001",
      status: "uploaded",
      signatureDate: null,
      startDate: null,
      endDate: null,
      termMonths: 36,
      isActive: false,
      activatedAt: null,
      lastAccessedAt: "2026-03-22T12:00:00Z",
      lastAnalyzedAt: "2026-03-21T12:00:00Z",
      parties: { entities: ["Loja Centro"] },
      financialTerms: { monthlyRent: 12000 },
      fieldConfidence: { signature_date: 0.95, parties: 0.87 },
    },
    selectedVersion,
    latestVersion: {
      contractVersionId: "ver-2",
      versionNumber: 2,
      createdAt: "2026-03-21T12:00:00Z",
      source: "third_party_draft" as const,
      originalFilename: "contract-v2.pdf",
      usedOcr: false,
      text: "Texto da versao 2",
    },
    selectedAnalysis: {
      analysisId: "ana-1",
      analysisStatus: "completed",
      policyVersion: "v1",
      contractRiskScore: 80,
      findings: [
        {
          id: "finding-1",
          clauseName: "Prazo de vigencia",
          status: "critical" as const,
          severity: "critical",
          currentSummary: "Prazo atual de 36 meses.",
          policyRule: "Prazo minimo exigido: 60 meses.",
          riskExplanation: "Prazo abaixo do minimo permitido pela politica.",
          suggestedAdjustmentDirection: "Solicitar prazo minimo de 60 meses.",
          metadata: {},
        },
      ],
      correctedReady,
    },
    events: [
      {
        id: "evt-1",
        eventType: "renewal" as const,
        eventDate: "2026-09-15",
        leadTimeDays: 30,
        metadata: {},
      },
    ],
    isCurrent: !isHistoricalView,
    isHistoricalView,
  };
}

function buildContractVersionsResponse() {
  return {
    items: [
      {
        contractVersionId: "ver-2",
        versionNumber: 2,
        createdAt: "2026-03-21T12:00:00Z",
        source: "third_party_draft" as const,
        originalFilename: "contract-v2.pdf",
        usedOcr: false,
        analysisStatus: "completed",
        contractRiskScore: 80,
        isCurrent: true,
      },
      {
        contractVersionId: "ver-1",
        versionNumber: 1,
        createdAt: "2026-03-20T12:00:00Z",
        source: "third_party_draft" as const,
        originalFilename: "contract-v1.pdf",
        usedOcr: false,
        analysisStatus: "completed",
        contractRiskScore: 92,
        isCurrent: false,
      },
    ],
  };
}

function buildVersionComparisonResponse() {
  return {
    selectedVersion: {
      contractVersionId: "ver-2",
      versionNumber: 2,
      createdAt: "2026-03-21T12:00:00Z",
      source: "third_party_draft" as const,
      originalFilename: "contract-v2.pdf",
      usedOcr: false,
      text: "Texto da versao 2",
    },
    baselineVersion: {
      contractVersionId: "ver-1",
      versionNumber: 1,
      createdAt: "2026-03-20T12:00:00Z",
      source: "third_party_draft" as const,
      originalFilename: "contract-v1.pdf",
      usedOcr: false,
      text: "Texto da versao 1",
    },
    summary: "A versao 2 corrige o prazo e adiciona fiador.",
    textDiff: {
      hasChanges: true,
      lines: [],
    },
    findingsDiff: {
      items: [],
    },
  };
}

describe("ContractDetailScreen", () => {
  it("shows a loading skeleton while detail data is pending", () => {
    render(
      <ContractDetailScreen
        contractId="ctr-1"
        loadContractDetail={() => new Promise(() => undefined)}
      />,
    );

    expect(screen.getByLabelText("Carregando conteudo")).toBeInTheDocument();
    expect(screen.getByText("Carregando contrato...")).toBeInTheDocument();
  });

  it("uses the canonical detail loader when no versionId is provided", async () => {
    const loadContractDetail = vi.fn().mockResolvedValue(buildContractDetail());
    const loadContractVersionDetail = vi.fn();

    render(
      <ContractDetailScreen
        contractId="ctr-1"
        loadContractDetail={loadContractDetail}
        loadContractVersionDetail={loadContractVersionDetail}
      />,
    );

    expect(await screen.findByRole("heading", { name: "Loja Centro" })).toBeInTheDocument();
    expect(loadContractDetail).toHaveBeenCalledWith("ctr-1");
    expect(loadContractVersionDetail).not.toHaveBeenCalled();
    expect(
      screen.getByText("Referência LOC-001 com leitura da versão atual do contrato."),
    ).toBeInTheDocument();
    expect(screen.getByText("Enviado")).toBeInTheDocument();
    expect(screen.getByText("Contrato padrão")).toBeInTheDocument();
    expect(screen.queryByText(/Política .* com status/i)).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Gerar Contrato Corrigido" })).toBeInTheDocument();
  });

  it("uses the version detail loader when versionId is provided", async () => {
    const loadContractDetail = vi.fn();
    const loadContractVersionDetail = vi
      .fn()
      .mockResolvedValue(buildContractDetail({ isHistoricalView: true }));

    render(
      <ContractDetailScreen
        contractId="ctr-1"
        versionId="ver-1"
        loadContractDetail={loadContractDetail}
        loadContractVersionDetail={loadContractVersionDetail}
      />,
    );

    expect(await screen.findByText("Versão histórica")).toBeInTheDocument();
    expect(loadContractVersionDetail).toHaveBeenCalledWith("ctr-1", "ver-1");
    expect(loadContractDetail).not.toHaveBeenCalled();
    expect(
      screen.getByText("Referência LOC-001 em leitura histórica da versão 1. A versão atual é a 2."),
    ).toBeInTheDocument();
  });

  it("shows an honest partial state when no selected analysis is available", async () => {
    const loadContractDetail = vi.fn().mockResolvedValue({
      ...buildContractDetail(),
      selectedAnalysis: null,
    });

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    expect(await screen.findByText("Análise ainda não disponível.")).toBeInTheDocument();
  });

  it("shows an honest partial state when no selected version is available", async () => {
    const loadContractDetail = vi.fn().mockResolvedValue({
      ...buildContractDetail(),
      selectedVersion: null,
      latestVersion: null,
    });

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    expect(await screen.findByText("Versão ainda não disponível.")).toBeInTheDocument();
  });

  it("shows a historical state explicitly and hides mutable actions", async () => {
    const loadContractVersionDetail = vi
      .fn()
      .mockResolvedValue(buildContractDetail({ isHistoricalView: true }));

    render(
      <ContractDetailScreen
        contractId="ctr-1"
        versionId="ver-1"
        loadContractVersionDetail={loadContractVersionDetail}
      />,
    );

    expect(await screen.findByText("Versão histórica")).toBeInTheDocument();
    expect(screen.getByText("Você está vendo a versão 1. A atual é a versão 2.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Gerar Contrato Corrigido" })).not.toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: "Baixar Contrato Corrigido (.docx)" }),
    ).not.toBeInTheDocument();
  });

  it("shows a not-found state when the backend returns 404", async () => {
    const loadContractDetail = vi
      .fn()
      .mockRejectedValue(new ContractsApiError("Contract not found", 404));

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    expect(
      await screen.findAllByRole("heading", { name: "Contrato não encontrado." }),
    ).toHaveLength(2);
    expect(
      screen.getByText("Revise a navegação da lista e tente abrir o contrato novamente."),
    ).toBeInTheDocument();
  });

  it("shows a transport error when detail loading fails", async () => {
    const loadContractDetail = vi
      .fn()
      .mockRejectedValue(new Error("Falha ao carregar o contrato."));

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Falha ao carregar o contrato.",
    );
  });

  it("retries the detail loading from the generic error state", async () => {
    const user = userEvent.setup();
    const loadContractDetail = vi
      .fn()
      .mockRejectedValueOnce(new Error("Falha ao carregar o contrato."))
      .mockResolvedValueOnce(buildContractDetail());

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Falha ao carregar o contrato.",
    );

    await user.click(screen.getByRole("button", { name: "Tentar novamente" }));

    expect(await screen.findByRole("heading", { name: "Loja Centro" })).toBeInTheDocument();
    expect(loadContractDetail).toHaveBeenCalledTimes(2);
  });

  it("does not render a manual refresh button in the contract detail header", async () => {
    const loadContractDetail = vi.fn().mockResolvedValue(buildContractDetail());

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    await screen.findByRole("heading", { name: "Loja Centro" });

    expect(screen.queryByRole("button", { name: "Atualizar detalhe" })).not.toBeInTheDocument();
  });

  it("renderiza metadados, eventos, resumo e texto da versao selecionada", async () => {
    const loadContractDetail = vi.fn().mockResolvedValue(buildContractDetail());

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    await screen.findByRole("heading", { name: "Loja Centro" });

    expect(screen.getByText("Metadados renderizados")).toBeInTheDocument();
    expect(screen.getByText("Renovação")).toBeInTheDocument();
    expect(screen.getByText("Resumo ctr-1 current")).toBeInTheDocument();
    expect(screen.getByText("Texto da versao 2")).toBeInTheDocument();
  });

  it("carrega o historico de versoes e o diff no detalhe do contrato", async () => {
    const loadContractDetail = vi.fn().mockResolvedValue(buildContractDetail());
    const loadContractVersions = vi.fn().mockResolvedValue(buildContractVersionsResponse());
    const compareVersions = vi.fn().mockResolvedValue(buildVersionComparisonResponse());

    render(
      <ContractDetailScreen
        contractId="ctr-1"
        loadContractDetail={loadContractDetail}
        loadContractVersions={loadContractVersions}
        compareVersions={compareVersions}
      />,
    );

    expect(await screen.findByText("Histórico de versões")).toBeInTheDocument();
    expect(screen.getByText("Versoes carregadas: 2, 1")).toBeInTheDocument();
    expect(screen.getByText("Painel de comparação")).toBeInTheDocument();
    expect(
      await screen.findByText("A versao 2 corrige o prazo e adiciona fiador."),
    ).toBeInTheDocument();
    expect(loadContractVersions).toHaveBeenCalledWith("ctr-1");
    expect(compareVersions).toHaveBeenCalledWith("ctr-1", {
      selectedVersionId: "ver-2",
      baselineVersionId: "ver-1",
    });
  });
});
