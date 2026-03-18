import React from "react";
import { render, screen } from "@testing-library/react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/font/google", () => ({
  DM_Sans: () => ({ className: "mocked-font" }),
}));

import RootLayout from "./layout";
import HomePage from "./page";

describe("HomePage", () => {
  it("renders the commercial hero, value sections and workspace CTAs", () => {
    render(<HomePage />);

    expect(screen.getByText("LegalTech")).toBeInTheDocument();
    expect(screen.getByText("Gestao contratual simplificada.")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Intake, triagem e acompanhamento de contratos em um unico workspace."
      )
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Abrir workspace" })).toHaveAttribute(
      "href",
      "/dashboard",
    );
    expect(
      screen.getByRole("heading", { name: "Do intake ao acompanhamento" })
    ).toBeInTheDocument();
    expect(screen.getByText("Intake estruturado")).toBeInTheDocument();
    expect(screen.getByText("Triagem por risco")).toBeInTheDocument();
    expect(screen.getByText("Acompanhamento executivo")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Organize seu portfolio contratual." })
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Comece agora" })).toHaveAttribute(
      "href",
      "/contracts",
    );
  });

  it("sets the application language to pt-BR", () => {
    const html = renderToStaticMarkup(
      <RootLayout>
        <div>child</div>
      </RootLayout>,
    );

    expect(html).toContain('lang="pt-BR"');
  });
});
