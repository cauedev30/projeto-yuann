import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ContractsScreen } from "./contracts-screen";

describe("ContractsScreen", () => {
  it("shows the empty state before any contract is uploaded", () => {
    render(<ContractsScreen submitContract={vi.fn()} />);

    expect(screen.getByText("Nenhum contrato enviado nesta sessao.")).toBeInTheDocument();
  });
});
