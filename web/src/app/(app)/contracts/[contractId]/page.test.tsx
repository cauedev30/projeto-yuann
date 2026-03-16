import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ContractDetailPage from "./page";

describe("ContractDetailPage", () => {
  it("keeps the placeholder content inside the shared contracts framing", async () => {
    const page = await ContractDetailPage({
      params: Promise.resolve({ contractId: "CTR-001" }),
    });

    render(page);

    expect(screen.getByText("Contracts")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "CTR-001" })).toBeInTheDocument();
    expect(
      screen.getByText("A timeline detalhada e os findings persistidos entram na proxima iteracao."),
    ).toBeInTheDocument();
  });
});
