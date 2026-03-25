import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../../../../features/contracts/screens/contract-detail-screen", () => ({
  ContractDetailScreen: ({
    contractId,
    versionId,
  }: {
    contractId: string;
    versionId?: string | null;
  }) => <div>Contract detail screen {contractId} {versionId ?? "current"}</div>,
}));

import ContractDetailPage from "./page";

describe("ContractDetailPage", () => {
  it("passes the route contract id to the detail screen composition root", async () => {
    const page = await ContractDetailPage({
      params: Promise.resolve({ contractId: "CTR-001" }),
      searchParams: Promise.resolve({}),
    });

    render(page);

    expect(screen.getByText("Contract detail screen CTR-001 current")).toBeInTheDocument();
  });

  it("passes versionId from search params to the detail screen", async () => {
    const page = await ContractDetailPage({
      params: Promise.resolve({ contractId: "CTR-001" }),
      searchParams: Promise.resolve({ versionId: "VER-002" }),
    });

    render(page);

    expect(screen.getByText("Contract detail screen CTR-001 VER-002")).toBeInTheDocument();
  });
});
