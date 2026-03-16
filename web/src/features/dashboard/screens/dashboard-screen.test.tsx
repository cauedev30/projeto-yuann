import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { buildDashboardSnapshotFixture } from "../fixtures/dashboard-snapshot";
import { DashboardScreen } from "./dashboard-screen";

describe("DashboardScreen", () => {
  it("frames the unavailable state with an executive header", () => {
    render(<DashboardScreen snapshot={null} />);

    expect(screen.getByText("Portifolio contratual")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Dashboard de renovacoes" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Dashboard indisponivel no momento.")).toBeInTheDocument();
  });

  it("renders summary, timeline and notification blocks when a snapshot exists", () => {
    render(<DashboardScreen snapshot={buildDashboardSnapshotFixture()} />);

    expect(screen.getByText("Resumo do portifolio")).toBeInTheDocument();
    expect(screen.getByText("Timeline de eventos")).toBeInTheDocument();
    expect(screen.getByText("Historico de notificacoes")).toBeInTheDocument();
  });
});
