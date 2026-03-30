import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { VersionDiffPanel } from "./version-diff-panel";

describe("VersionDiffPanel", () => {
  it("usa copy em portugues no estado vazio", () => {
    render(<VersionDiffPanel comparison={null} isLoading={false} errorMessage={null} />);

    expect(screen.getByRole("heading", { name: "Painel de comparação" })).toBeInTheDocument();
    expect(screen.getByText("Nenhuma comparação selecionada.")).toBeInTheDocument();
    expect(screen.queryByText("Painel de diff")).not.toBeInTheDocument();
  });
});
