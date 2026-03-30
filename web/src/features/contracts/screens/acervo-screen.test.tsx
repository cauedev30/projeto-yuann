import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { ContractDetail } from "../../../entities/contracts/model";
import { listContracts, updateContract } from "../../../lib/api/contracts";
import { AcervoScreen } from "./acervo-screen";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("../../../lib/api/contracts", () => ({
  listContracts: vi.fn(),
  updateContract: vi.fn(),
}));

function buildActiveContractsResult() {
  return {
    items: [
      {
        id: "ctr-active",
        title: "Contrato Ativo",
        externalReference: "ACT-001",
        status: "uploaded",
        signatureDate: null,
        startDate: null,
        endDate: null,
        termMonths: 12,
        isActive: true,
        activatedAt: "2026-03-20T10:00:00Z",
        lastAccessedAt: "2026-03-21T10:00:00Z",
        lastAnalyzedAt: "2026-03-20T10:00:00Z",
        latestAnalysisStatus: "completed",
        latestRiskScore: 20,
        latestVersionSource: "signed_contract" as const,
      },
    ],
  };
}

function buildUpdatedContractDetail(): ContractDetail {
  return {
    contract: {
      id: "ctr-active",
      title: "Contrato Ativo",
      externalReference: "ACT-001",
      status: "uploaded",
      signatureDate: null,
      startDate: null,
      endDate: null,
      termMonths: 12,
      isActive: false,
      activatedAt: null,
      lastAccessedAt: null,
      lastAnalyzedAt: null,
      parties: null,
      financialTerms: null,
      fieldConfidence: {},
    },
    selectedVersion: null,
    latestVersion: null,
    selectedAnalysis: null,
    events: [],
    isCurrent: true,
    isHistoricalView: false,
  };
}

describe("AcervoScreen", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state initially", async () => {
    vi.mocked(listContracts).mockReturnValue(new Promise(() => {}));
    render(<AcervoScreen />);
    
    expect(screen.getByText("Contratos Vigentes")).toBeInTheDocument();
    expect(screen.getByLabelText("Carregando lista")).toBeInTheDocument();
  });

  it("shows error state", async () => {
    vi.mocked(listContracts).mockRejectedValue(new Error("Erro de conexão"));
    render(<AcervoScreen />);
    
    expect(await screen.findByRole("alert")).toHaveTextContent("Erro de conexão");
  });

  it("shows empty state", async () => {
    vi.mocked(listContracts).mockResolvedValue({ items: [] });
    render(<AcervoScreen />);
    
    expect(await screen.findByText("Acervo vazio")).toBeInTheDocument();
  });

  it("renders active contracts", async () => {
    vi.mocked(listContracts).mockResolvedValue(buildActiveContractsResult());
    render(<AcervoScreen />);
    
    expect(await screen.findByText("Contrato Ativo")).toBeInTheDocument();
    expect(screen.getByText("Ref: ACT-001")).toBeInTheDocument();
    expect(screen.queryByText(/pontuação/i)).not.toBeInTheDocument();
  });

  it("calls updateContract to deactivate and refreshes", async () => {
    const user = userEvent.setup();
    vi.mocked(listContracts).mockResolvedValue(buildActiveContractsResult());
    vi.mocked(updateContract).mockResolvedValue(buildUpdatedContractDetail());

    render(<AcervoScreen />);
    
    const button = await screen.findByRole("button", { name: "Desativar" });
    await user.click(button);

    expect(updateContract).toHaveBeenCalledWith("ctr-active", { isActive: false });
    expect(listContracts).toHaveBeenCalledTimes(2); // Initial + refresh
  });
});
