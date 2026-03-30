import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getContractSummary } from "../../../lib/api/contracts";
import { ContractSummaryPanel } from "./contract-summary-panel";

vi.mock("../../../lib/api/contracts", () => ({
  getContractSummary: vi.fn(),
}));

describe("ContractSummaryPanel", () => {
  beforeEach(() => {
    vi.mocked(getContractSummary).mockReset();
  });

  it("renderiza apenas o resumo em PT-BR, sem exibir a lista de principais pontos", async () => {
    vi.mocked(getContractSummary).mockResolvedValue({
      summary: "Prazo contratual de 36 meses.\n\nReajuste anual pelo IPCA.",
      key_points: [
        "Prazo abaixo do alvo de 60 meses.",
        "Reajuste monetário anual previsto no texto.",
      ],
    });

    render(<ContractSummaryPanel contractId="ctr-1" />);

    expect(await screen.findByText("Prazo contratual de 36 meses.")).toBeInTheDocument();
    expect(screen.getByText("Reajuste anual pelo IPCA.")).toBeInTheDocument();
    expect(screen.queryByText("Principais pontos")).not.toBeInTheDocument();
    expect(screen.queryByText("Prazo abaixo do alvo de 60 meses.")).not.toBeInTheDocument();
    expect(screen.queryByText("Reajuste monetário anual previsto no texto.")).not.toBeInTheDocument();
  });

  it("encaminha versionId ao buscar o resumo", async () => {
    vi.mocked(getContractSummary).mockResolvedValue({
      summary: "Resumo da versão histórica.",
      key_points: [],
    });

    render(<ContractSummaryPanel contractId="ctr-1" versionId="ver-1" />);

    await waitFor(() => expect(getContractSummary).toHaveBeenCalledWith("ctr-1", "ver-1"));
  });

  it("mostra estado honesto quando o resumo ainda não está disponível", async () => {
    vi.mocked(getContractSummary).mockResolvedValue({
      summary: "",
      key_points: [],
    });

    render(<ContractSummaryPanel contractId="ctr-1" />);

    expect(await screen.findByText("Resumo ainda não disponível.")).toBeInTheDocument();
  });

  it("permite tentar novamente após erro de carregamento", async () => {
    const user = userEvent.setup();
    vi.mocked(getContractSummary)
      .mockRejectedValueOnce(new Error("Falha ao gerar o resumo."))
      .mockResolvedValueOnce({
        summary: "Resumo recuperado.",
        key_points: ["Ponto restaurado."],
      });

    render(<ContractSummaryPanel contractId="ctr-1" />);

    expect(await screen.findByText("Falha ao gerar o resumo.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Tentar novamente" }));

    expect(await screen.findByText("Resumo recuperado.")).toBeInTheDocument();
    expect(getContractSummary).toHaveBeenCalledTimes(2);
  });
});
