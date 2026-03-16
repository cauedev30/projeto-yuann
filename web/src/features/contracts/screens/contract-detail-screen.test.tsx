import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ContractsApiError } from "../../../lib/api/contracts";
import { ContractDetailScreen } from "./contract-detail-screen";

function buildContractDetail() {
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
      parties: { tenant: "Loja Centro" },
      financialTerms: { monthlyRent: 12000 },
    },
    latestVersion: {
      contractVersionId: "ver-1",
      source: "third_party_draft" as const,
      originalFilename: "contract.pdf",
      usedOcr: false,
      text: "Prazo de vigencia 36 meses",
    },
    latestAnalysis: {
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
    },
  };
}

describe("ContractDetailScreen", () => {
  it("renders the latest analysis findings when available", async () => {
    const loadContractDetail = vi.fn().mockResolvedValue(buildContractDetail());

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    expect(await screen.findByRole("heading", { name: "Loja Centro" })).toBeInTheDocument();
    expect(screen.getByText("Prazo de vigencia")).toBeInTheDocument();
    expect(screen.getByText("contract.pdf")).toBeInTheDocument();
  });

  it("shows an honest partial state when no latest analysis is available", async () => {
    const loadContractDetail = vi.fn().mockResolvedValue({
      ...buildContractDetail(),
      latestAnalysis: null,
    });

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    expect(await screen.findByText("Analise ainda nao disponivel.")).toBeInTheDocument();
  });

  it("shows an honest partial state when no latest version is available", async () => {
    const loadContractDetail = vi.fn().mockResolvedValue({
      ...buildContractDetail(),
      latestVersion: null,
    });

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    expect(await screen.findByText("Versao ainda nao disponivel.")).toBeInTheDocument();
  });

  it("shows a not-found state when the backend returns 404", async () => {
    const loadContractDetail = vi
      .fn()
      .mockRejectedValue(new ContractsApiError("Contract not found", 404));

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    expect(
      await screen.findAllByRole("heading", { name: "Contrato nao encontrado." }),
    ).toHaveLength(2);
    expect(
      screen.getByText("Revise a navegacao da lista e tente abrir o contrato novamente."),
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

  it("refreshes the contract detail on demand", async () => {
    const user = userEvent.setup();
    const loadContractDetail = vi.fn().mockResolvedValue(buildContractDetail());

    render(
      <ContractDetailScreen contractId="ctr-1" loadContractDetail={loadContractDetail} />,
    );

    await screen.findByRole("heading", { name: "Loja Centro" });
    await user.click(screen.getByRole("button", { name: "Atualizar detalhe" }));

    await waitFor(() => expect(loadContractDetail).toHaveBeenCalledTimes(2));
  });
});
