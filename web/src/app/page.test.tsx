import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "./page";

describe("HomePage", () => {
  it("renders the commercial hero, value sections and workspace CTAs", () => {
    render(<HomePage />);

    expect(
      screen.getByRole("heading", {
        name: "Governanca contratual para times de expansao",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Entrar no workspace" }),
    ).toHaveAttribute("href", "/dashboard");
    expect(
      screen.getByRole("heading", { name: "Do intake ao acompanhamento" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Upload e triagem inicial")).toBeInTheDocument();
    expect(screen.getByText("Monitoramento de eventos")).toBeInTheDocument();
  });
});
