import React from "react";
import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { ClauseStepper } from "./clause-stepper";
import type { ContractFinding } from "../../../entities/contracts/model";

const baseFinding: ContractFinding = {
  clauseName: "OBJETO_E_VIABILIDADE",
  status: "conforme",
  currentSummary: "Texto atual da clausula",
  policyRule: "Regra da policy",
  riskExplanation: "Sem risco",
  suggestedAdjustmentDirection: "",
};

const criticalFinding: ContractFinding = {
  clauseName: "PRAZO_E_RENOVACAO",
  status: "critical",
  currentSummary: "Prazo abaixo do minimo",
  policyRule: "Prazo minimo de 60 meses",
  riskExplanation: "Risco de prazo curto",
  suggestedAdjustmentDirection: "Aumentar prazo",
};

const attentionFinding: ContractFinding = {
  clauseName: "EXCLUSIVIDADE",
  status: "attention",
  currentSummary: "Clausula de exclusividade presente",
  policyRule: "Exclusividade deve ser limitada",
  riskExplanation: "Exclusividade ampla",
  suggestedAdjustmentDirection: "Limitar escopo",
};

const nineFindings: ContractFinding[] = Array.from({ length: 9 }, (_, i) => ({
  ...baseFinding,
  clauseName: [
    "OBJETO_E_VIABILIDADE", "EXCLUSIVIDADE", "OBRAS_E_ADAPTACOES",
    "CESSAO_E_SUBLOCACAO", "PRAZO_E_RENOVACAO", "COMUNICACAO_E_PENALIDADES",
    "OBRIGACAO_DE_NAO_FAZER", "VISTORIA_E_ACESSO", "ASSINATURA_E_FORMA",
  ][i],
}));

describe("ClauseStepper", () => {
  it("renders one clause at a time", () => {
    render(<ClauseStepper findings={nineFindings} />);
    expect(screen.getByText("Cláusula 1 de 9")).toBeInTheDocument();
    expect(screen.getByText("Objeto e Viabilidade")).toBeInTheDocument();
  });

  it("navigates to next clause with button", () => {
    render(<ClauseStepper findings={nineFindings} />);
    const nextButtons = screen.getAllByRole("button").filter(b => b.textContent?.includes("Próximo"));
    fireEvent.click(nextButtons[0]);
    expect(screen.getByText("Cláusula 2 de 9")).toBeInTheDocument();
    expect(screen.getByText("Exclusividade")).toBeInTheDocument();
  });

  it("navigates back with button", () => {
    render(<ClauseStepper findings={nineFindings} />);
    const nextButtons = screen.getAllByRole("button").filter(b => b.textContent?.includes("Próximo"));
    fireEvent.click(nextButtons[0]);
    const prevButtons = screen.getAllByRole("button").filter(b => b.textContent?.includes("Anterior"));
    fireEvent.click(prevButtons[0]);
    expect(screen.getByText("Cláusula 1 de 9")).toBeInTheDocument();
  });

  it("disables Anterior on first clause", () => {
    render(<ClauseStepper findings={nineFindings} />);
    const prevButtons = screen.getAllByRole("button").filter(b => b.textContent?.includes("Anterior"));
    expect(prevButtons[0]).toBeDisabled();
  });

  it("shows verdict after last clause", () => {
    render(<ClauseStepper findings={[baseFinding]} />);
    const verdictButton = screen.getByLabelText("Veredito final");
    fireEvent.click(verdictButton);
    expect(screen.getByText("Veredito Final")).toBeInTheDocument();
  });

  it("hides suggestions in acervo context", () => {
    render(<ClauseStepper findings={[criticalFinding]} context="acervo" />);
    expect(screen.queryByText("Direção sugerida:")).not.toBeInTheDocument();
  });

  it("shows suggestions in historico context for critical findings", () => {
    render(<ClauseStepper findings={[criticalFinding]} context="historico" />);
    expect(screen.getByText("Aumentar prazo")).toBeInTheDocument();
  });

  it("shows suggestions in historico context for attention findings", () => {
    render(<ClauseStepper findings={[attentionFinding]} context="historico" />);
    expect(screen.getByText("Limitar escopo")).toBeInTheDocument();
  });

  it("renders dots reflecting severity", () => {
    const { container } = render(
      <ClauseStepper findings={[criticalFinding, attentionFinding, baseFinding]} />
    );
    const dots = container.querySelectorAll("[class*='dot-']");
    expect(dots.length).toBeGreaterThanOrEqual(3);
  });

  it("navigates to verdict via verdict dot button", () => {
    render(<ClauseStepper findings={[baseFinding]} />);
    const verdictButton = screen.getByLabelText("Veredito final");
    fireEvent.click(verdictButton);
    expect(screen.getByText("Veredito Final")).toBeInTheDocument();
  });

  it("shows classification badge from metadata", () => {
    const findingWithClassification: ContractFinding = {
      ...baseFinding,
      metadata: { classification: "ausente" },
    };
    render(<ClauseStepper findings={[findingWithClassification]} />);
    expect(screen.getByText("Ausente")).toBeInTheDocument();
  });
});