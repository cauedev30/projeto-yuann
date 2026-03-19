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
        "Entrada, triagem e acompanhamento de contratos em um unico espaço de trabalho."
      )
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Abrir espaço de trabalho" })).toHaveAttribute(
      "href",
      "/dashboard",
    );
    expect(
      screen.getByRole("heading", { name: "Da entrada ao acompanhamento" })
    ).toBeInTheDocument();
    expect(screen.getByText("Entrada estruturada")).toBeInTheDocument();
    expect(screen.getByText("Triagem por risco")).toBeInTheDocument();
    expect(screen.getByText("Acompanhamento executivo")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Organize seu portfólio contratual." })
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
