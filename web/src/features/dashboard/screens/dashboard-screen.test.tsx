import React from "react";
import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { buildDashboardSnapshotFixture } from "../fixtures/dashboard-snapshot";
import { DashboardScreen } from "./dashboard-screen";

describe("DashboardScreen", () => {
  it("shows an explicit unavailable state when no runtime dashboard snapshot exists", () => {
    render(<DashboardScreen snapshot={null} />);

    expect(screen.getByText("Dashboard indisponivel no momento.")).toBeInTheDocument();
  });

  it("renders dashboard data when a test fixture snapshot is provided", () => {
    const { container } = render(<DashboardScreen snapshot={buildDashboardSnapshotFixture()} />);

    expect(within(container).getByText("Timeline de eventos")).toBeInTheDocument();
    expect(within(container).getByText("alerts@example.com")).toBeInTheDocument();
  });
});
