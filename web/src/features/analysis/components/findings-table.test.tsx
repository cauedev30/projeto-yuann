import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { FindingsTable } from "./findings-table";


describe("FindingsTable", () => {
  it("renders an accessible findings table with explicit column headers", () => {
    render(
      <FindingsTable
        items={[
          {
            clauseName: "Prazo de vigencia",
            status: "critical",
            riskExplanation: "Prazo abaixo do minimo permitido",
            currentSummary: "Prazo atual de 36 meses.",
            policyRule: "Prazo minimo exigido: 60 meses.",
            suggestedAdjustmentDirection: "Solicitar prazo minimo de 60 meses.",
          },
        ]}
      />,
    );

    expect(screen.getByRole("table", { name: "Tabela de findings" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Clausula" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Status" })).toBeInTheDocument();
    expect(screen.getByText("critical")).toBeInTheDocument();
    expect(screen.getByText("Prazo de vigencia")).toBeInTheDocument();
  });
});
