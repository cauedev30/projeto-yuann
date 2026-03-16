import React from "react";
import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

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

    expect(navigation).toBeInTheDocument();
    expect(within(navigation).getByRole("link", { name: "Dashboard" })).toHaveAttribute(
      "href",
      "/dashboard",
    );
    expect(within(navigation).getByRole("link", { name: "Contracts" })).toHaveAttribute(
      "href",
      "/contracts",
    );
    expect(screen.getByText("Conteudo interno")).toBeInTheDocument();
  });
});
