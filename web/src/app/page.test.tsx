import React from "react";
import { render, screen } from "@testing-library/react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import RootLayout from "./layout";
import HomePage from "./page";

describe("HomePage", () => {
  it("renders the commercial hero, value sections and workspace CTAs", () => {
    render(<HomePage />);

    expect(screen.getByText("LegalTech")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        name: "A materia contratual em formato de decisao.",
      }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Abrir workspace" })).toHaveAttribute(
      "href",
      "/dashboard",
    );
    expect(
      screen.getByRole("heading", { name: "Do intake ao acompanhamento" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Leitura juridica, trilha operacional e proximas acoes em uma mesma cadencia visual.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Triagem orientada por risco")).toBeInTheDocument();
    expect(screen.getByText("Acompanhamento com trilha executiva")).toBeInTheDocument();
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
