import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { VersionHistoryPanel } from "./version-history-panel";

describe("VersionHistoryPanel", () => {
  it("renderiza o horario da versao formatado em pt-BR em vez do ISO cru", () => {
    const formattedTimestamp = new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date("2026-03-30T02:49:36"));

    render(
      <VersionHistoryPanel
        versions={[
          {
            contractVersionId: "ver-1",
            versionNumber: 1,
            createdAt: "2026-03-30T02:49:36",
            source: "third_party_draft",
            originalFilename: "contrato-v1.pdf",
            usedOcr: false,
            analysisStatus: null,
            contractRiskScore: null,
            isCurrent: true,
          },
        ]}
        isLoading={false}
        errorMessage={null}
        selectedVersionId="ver-1"
        comparisonBaselineId={null}
        onOpenVersion={vi.fn()}
        onCompareWith={vi.fn()}
      />,
    );

    expect(screen.getByText(`contrato-v1.pdf · ${formattedTimestamp}`)).toBeInTheDocument();
    expect(screen.queryByText(/2026-03-30T02:49:36/)).not.toBeInTheDocument();
  });

  it("usa terminologia em portugues para a base de comparacao", () => {
    render(
      <VersionHistoryPanel
        versions={[
          {
            contractVersionId: "ver-1",
            versionNumber: 1,
            createdAt: "2026-03-30T02:49:36",
            source: "third_party_draft",
            originalFilename: "contrato-v1.pdf",
            usedOcr: false,
            analysisStatus: null,
            contractRiskScore: null,
            isCurrent: false,
          },
        ]}
        isLoading={false}
        errorMessage={null}
        selectedVersionId={null}
        comparisonBaselineId="ver-1"
        onOpenVersion={vi.fn()}
        onCompareWith={vi.fn()}
      />,
    );

    expect(screen.getByText("Base de comparação")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Usar como base de comparação" })).toBeInTheDocument();
    expect(screen.queryByText("Baseline")).not.toBeInTheDocument();
  });
});
