import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../../../../features/contracts/screens/contract-detail-screen", () => ({
  ContractDetailScreen: ({ contractId }: { contractId: string }) => (
    <div>Contract detail screen {contractId}</div>
  ),
}));

import ContractDetailPage from "./page";

describe("ContractDetailPage", () => {
  it("passes the route contract id to the detail screen composition root", async () => {
    const page = await ContractDetailPage({
      params: Promise.resolve({ contractId: "CTR-001" }),
    });

    render(page);

    expect(screen.getByText("Contract detail screen CTR-001")).toBeInTheDocument();
  });
});
