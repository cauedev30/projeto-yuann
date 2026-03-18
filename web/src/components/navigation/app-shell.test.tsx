import React from "react";
import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
}));

import { AppShell } from "./app-shell";

describe("AppShell", () => {
  it("renders the primary workspace navigation and the content region", () => {
    render(
      <AppShell>
        <div>Conteudo interno</div>
      </AppShell>,
    );

    const navigation = screen.getByRole("navigation", {
      name: "Navegacao principal do workspace",
    });
    const contentRegion = screen.getByRole("main");

    expect(
      screen.getByRole("link", { name: "Pular para o conteudo principal" }),
    ).toHaveAttribute("href", "#main-content");
    expect(navigation).toBeInTheDocument();
    expect(contentRegion).toHaveAttribute("id", "main-content");
    expect(screen.getByRole("link", { name: "LegalTech" })).toHaveAttribute("href", "/");
    expect(within(navigation).getByRole("link", { name: "Dashboard" })).toHaveAttribute(
      "href",
      "/dashboard",
    );
    expect(within(navigation).getByRole("link", { name: "Contracts" })).toHaveAttribute(
      "href",
      "/contracts",
    );
    expect(screen.getAllByText("Governanca contratual").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Conteudo interno")).toBeInTheDocument();
  });
});
