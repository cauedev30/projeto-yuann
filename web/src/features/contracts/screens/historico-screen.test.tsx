import React from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { listContracts, updateContract } from "../../../lib/api/contracts";
import { HistoricoScreen } from "./historico-screen";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("../../../lib/api/contracts", () => ({
  listContracts: vi.fn(),
  updateContract: vi.fn(),
}));

function buildHistoryContractsResult(lastAnalyzedDaysAgo: number = 5) {
  const d = new Date();
  d.setDate(d.getDate() - lastAnalyzedDaysAgo);

  return {
    items: [
      {
        id: "ctr-hist",
        title: "Contrato Histórico",
        externalReference: "HST-001",
        status: "uploaded",
        signatureDate: null,
        startDate: null,
        endDate: null,
        termMonths: 24,
        isActive: false,
        activatedAt: null,
        lastAccessedAt: new Date().toISOString(),
        lastAnalyzedAt: d.toISOString(),
        latestAnalysisStatus: "completed",
        latestRiskScore: 50,
        latestVersionSource: "signed_contract" as const,
      },
    ],
  };
}

describe("HistoricoScreen", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state initially", async () => {
    vi.mocked(listContracts).mockReturnValue(new Promise(() => {}));
    render(<HistoricoScreen />);
    
    expect(screen.getByText("Contratos Analisados")).toBeInTheDocument();
    expect(screen.getByLabelText("Carregando lista")).toBeInTheDocument();
  });

  it("shows error state", async () => {
    vi.mocked(listContracts).mockRejectedValue(new Error("Erro de histórico"));
    render(<HistoricoScreen />);
    
    expect(await screen.findByRole("alert")).toHaveTextContent("Erro de histórico");
  });

  it("shows empty state", async () => {
    vi.mocked(listContracts).mockResolvedValue({ items: [] });
    render(<HistoricoScreen />);
    
    expect(await screen.findByText("Histórico vazio")).toBeInTheDocument();
  });

  it("renders history contracts with metadata", async () => {
    vi.mocked(listContracts).mockResolvedValue(buildHistoryContractsResult(5));
    render(<HistoricoScreen />);
    
    expect(await screen.findByText("Contrato Histórico")).toBeInTheDocument();
    
    const analysisDateStr = new Date(new Date().setDate(new Date().getDate() - 5)).toLocaleDateString("pt-BR");
    expect(screen.getByText(`Última análise: ${analysisDateStr}`)).toBeInTheDocument();
    
    const accessDateStr = new Date().toLocaleDateString("pt-BR");
    expect(screen.getByText(`Último acesso: ${accessDateStr}`)).toBeInTheDocument();
    
    expect(screen.getByText("Expira em 25 dias")).toBeInTheDocument();
  });

  it("renders expiration correctly when expired", async () => {
    vi.mocked(listContracts).mockResolvedValue(buildHistoryContractsResult(35));
    render(<HistoricoScreen />);
    
    expect(await screen.findByText("Expirado")).toBeInTheDocument();
  });

  it("calls updateContract to activate and refreshes", async () => {
    const user = userEvent.setup();
    vi.mocked(listContracts).mockResolvedValue(buildHistoryContractsResult(5));
    vi.mocked(updateContract).mockResolvedValue({} as any);

    render(<HistoricoScreen />);
    
    const button = await screen.findByRole("button", { name: "Ativar" });
    await user.click(button);

    expect(updateContract).toHaveBeenCalledWith("ctr-hist", { isActive: true });
    expect(listContracts).toHaveBeenCalledTimes(2); // Initial + refresh
  });
});
