import React from "react";
import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MetadataSection } from "./metadata-section";

const defaultProps = {
  parties: { entities: ["Empresa Alpha Ltda", "Locadora Beta S.A."] },
  financialTerms: { grace_period_months: 3, readjustment_type: "IPCA" },
  fieldConfidence: {},
  signatureDate: "2024-01-15",
  startDate: "2024-02-01",
  endDate: "2025-01-31",
};

describe("MetadataSection", () => {
  it("renders explicit contract roles when they are available", () => {
    render(
      <MetadataSection
        {...defaultProps}
        parties={{
          entities: ["Empresa Alpha Ltda", "Locadora Beta S.A."],
          locatario: "Empresa Alpha Ltda",
          locador: "Locadora Beta S.A.",
          fiador: "Joao da Silva",
        }}
      />,
    );

    expect(screen.getByText("Locatário")).toBeInTheDocument();
    expect(screen.getByText("Empresa Alpha Ltda")).toBeInTheDocument();
    expect(screen.getByText("Locador")).toBeInTheDocument();
    expect(screen.getByText("Locadora Beta S.A.")).toBeInTheDocument();
    expect(screen.getByText("Fiador")).toBeInTheDocument();
    expect(screen.getByText("Joao da Silva")).toBeInTheDocument();
  });

  it("renders generic party entities as readable text, not JSON", () => {
    const { container } = render(<MetadataSection {...defaultProps} />);
    expect(within(container).getByText("Empresa Alpha Ltda")).toBeInTheDocument();
    expect(within(container).getByText("Locadora Beta S.A.")).toBeInTheDocument();
    expect(container.textContent).not.toContain("JSON.stringify");
    expect(container.textContent).not.toContain('{"entities"');
  });

  it("does not render the signature date row anymore", () => {
    render(<MetadataSection {...defaultProps} />);
    expect(screen.queryByText("Data de assinatura")).not.toBeInTheDocument();
    expect(screen.queryByText("15/01/2024")).not.toBeInTheDocument();
  });

  it("renders startDate in DD/MM/YYYY format", () => {
    render(<MetadataSection {...defaultProps} />);
    expect(screen.getByText("01/02/2024")).toBeInTheDocument();
  });

  it("renders endDate in DD/MM/YYYY format", () => {
    render(<MetadataSection {...defaultProps} />);
    expect(screen.getByText("31/01/2025")).toBeInTheDocument();
  });

  it("renders financial terms with PT-BR labels", () => {
    render(
      <MetadataSection
        {...defaultProps}
        financialTerms={{
          grace_period_months: 3,
          readjustment_type: "annual",
          monthly_rent: 12000,
          penalty_months: 3,
        }}
      />,
    );

    expect(screen.getByText("Carência")).toBeInTheDocument();
    expect(screen.getByText("Tipo de reajuste")).toBeInTheDocument();
    expect(screen.getByText("Aluguel")).toBeInTheDocument();
    expect(screen.getByText("Multa (meses)")).toBeInTheDocument();
    expect(screen.getByText("Anual")).toBeInTheDocument();
  });

  it("shows Alta confidence pill when fieldConfidence >= 0.8", () => {
    render(<MetadataSection {...defaultProps} fieldConfidence={{ parties: 0.95 }} />);
    expect(screen.getByText("Alta")).toBeInTheDocument();
  });

  it("shows Media confidence pill when fieldConfidence >= 0.5 and < 0.8", () => {
    render(<MetadataSection {...defaultProps} fieldConfidence={{ parties: 0.65 }} />);
    expect(screen.getByText("Média")).toBeInTheDocument();
  });

  it("shows Baixa confidence pill when fieldConfidence < 0.5", () => {
    render(<MetadataSection {...defaultProps} fieldConfidence={{ parties: 0.3 }} />);
    expect(screen.getByText("Baixa")).toBeInTheDocument();
  });

  it("shows Não identificado when parties is null", () => {
    render(<MetadataSection {...defaultProps} parties={null} />);
    expect(screen.getAllByText("Não identificado").length).toBeGreaterThanOrEqual(1);
  });

  it("keeps signatureDate hidden even when it is null", () => {
    render(<MetadataSection {...defaultProps} signatureDate={null} />);
    expect(screen.queryByText("Data de assinatura")).not.toBeInTheDocument();
  });

  it("shows Sem termos financeiros when financialTerms is null", () => {
    render(<MetadataSection {...defaultProps} financialTerms={null} />);
    expect(screen.getByText("Sem termos financeiros")).toBeInTheDocument();
  });

  it("shows unknown financial term keys as readable labels", () => {
    render(<MetadataSection {...defaultProps} financialTerms={{ custom_fee: "R$ 500" }} />);
    expect(screen.getByText("Custom fee")).toBeInTheDocument();
    expect(screen.queryByText("custom_fee")).not.toBeInTheDocument();
    expect(screen.getByText("R$ 500")).toBeInTheDocument();
  });
});
