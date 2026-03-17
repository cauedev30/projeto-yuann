import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { buildDashboardSnapshotFixture } from "../fixtures/dashboard-snapshot";
import { DashboardScreen } from "./dashboard-screen";

describe("DashboardScreen", () => {
  it("shows a loading state before rendering the dashboard result", () => {
    render(<DashboardScreen loadDashboardSnapshot={() => new Promise(() => undefined)} />);

    expect(screen.getByText("Mesa juridica")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Governanca contratual em andamento" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Carregando dashboard operacional...")).toBeInTheDocument();
  });

  it("frames the unavailable state with an executive header", async () => {
    render(<DashboardScreen loadDashboardSnapshot={async () => null} />);

    expect(await screen.findByText("Dashboard indisponivel no momento.")).toBeInTheDocument();
  });

  it("renders an error state when the dashboard request fails", async () => {
    render(
      <DashboardScreen
        loadDashboardSnapshot={async () => {
          throw new Error("Falha de integracao.");
        }}
      />,
    );

    expect(await screen.findByRole("alert")).toHaveTextContent("Falha de integracao.");
  });

  it("renders summary, timeline and notification blocks when a snapshot exists", async () => {
    render(<DashboardScreen loadDashboardSnapshot={async () => buildDashboardSnapshotFixture()} />);

    expect(await screen.findByText("Resumo do portifolio")).toBeInTheDocument();
    expect(screen.getByText("Timeline de eventos")).toBeInTheDocument();
    expect(screen.getByText("Historico de notificacoes")).toBeInTheDocument();
  });
});
