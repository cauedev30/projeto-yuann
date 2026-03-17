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
  it("renders party names as readable text, not JSON", () => {
    const { container } = render(<MetadataSection {...defaultProps} />);
    expect(within(container).getByText("Empresa Alpha Ltda")).toBeInTheDocument();
    expect(within(container).getByText("Locadora Beta S.A.")).toBeInTheDocument();
    expect(container.textContent).not.toContain("JSON.stringify");
    expect(container.textContent).not.toContain('{"entities"');
  });

  it("renders signatureDate in DD/MM/YYYY format", () => {
    const { container } = render(<MetadataSection {...defaultProps} />);
    expect(within(container).getByText("15/01/2024")).toBeInTheDocument();
  });

  it("renders startDate in DD/MM/YYYY format", () => {
    const { container } = render(<MetadataSection {...defaultProps} />);
    expect(within(container).getByText("01/02/2024")).toBeInTheDocument();
  });

  it("renders endDate in DD/MM/YYYY format", () => {
    const { container } = render(<MetadataSection {...defaultProps} />);
    expect(within(container).getByText("31/01/2025")).toBeInTheDocument();
  });

  it("renders financial terms with PT-BR labels", () => {
    const { container } = render(<MetadataSection {...defaultProps} />);
    expect(within(container).getByText("Carência")).toBeInTheDocument();
    expect(within(container).getByText("Tipo de reajuste")).toBeInTheDocument();
    expect(within(container).getByText("IPCA")).toBeInTheDocument();
  });

  it("shows Alta confidence pill when fieldConfidence >= 0.8", () => {
    render(
      <MetadataSection
        {...defaultProps}
        fieldConfidence={{ parties: 0.95 }}
      />,
    );
    expect(screen.getByText("Alta")).toBeInTheDocument();
  });

  it("shows Média confidence pill when fieldConfidence >= 0.5 and < 0.8", () => {
    render(
      <MetadataSection
        {...defaultProps}
        fieldConfidence={{ parties: 0.65 }}
      />,
    );
    expect(screen.getByText("Média")).toBeInTheDocument();
  });

  it("shows Baixa confidence pill when fieldConfidence < 0.5", () => {
    render(
      <MetadataSection
        {...defaultProps}
        fieldConfidence={{ parties: 0.3 }}
      />,
    );
    expect(screen.getByText("Baixa")).toBeInTheDocument();
  });

  it("shows Não identificado when parties is null", () => {
    const { container } = render(
      <MetadataSection {...defaultProps} parties={null} />,
    );
    const allNotIdentified = within(container).getAllByText("Não identificado");
    expect(allNotIdentified.length).toBeGreaterThanOrEqual(1);
  });

  it("shows Não identificado when signatureDate is null", () => {
    const { container } = render(
      <MetadataSection {...defaultProps} signatureDate={null} />,
    );
    const allNotIdentified = within(container).getAllByText("Não identificado");
    expect(allNotIdentified.length).toBeGreaterThanOrEqual(1);
  });

  it("shows Sem termos financeiros when financialTerms is null", () => {
    const { container } = render(
      <MetadataSection {...defaultProps} financialTerms={null} />,
    );
    expect(within(container).getByText("Sem termos financeiros")).toBeInTheDocument();
  });

  it("shows unknown financial term keys as-is", () => {
    const { container } = render(
      <MetadataSection
        {...defaultProps}
        financialTerms={{ custom_fee: "R$ 500" }}
      />,
    );
    expect(within(container).getByText("custom_fee")).toBeInTheDocument();
    expect(within(container).getByText("R$ 500")).toBeInTheDocument();
  });
});
