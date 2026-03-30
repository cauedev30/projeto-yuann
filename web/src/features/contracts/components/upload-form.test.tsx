import React from "react";
import { render, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { UploadForm } from "./upload-form";


describe("UploadForm", () => {
  it("keeps the submit button disabled until a pdf is selected", () => {
    const view = render(<UploadForm onSubmit={vi.fn()} isSubmitting={false} />);
    const scope = within(view.container);

    expect(scope.getByRole("button", { name: "Enviar contrato" })).toBeDisabled();
  });

  it("shows human-readable contract type labels", () => {
    const view = render(<UploadForm onSubmit={vi.fn()} isSubmitting={false} />);
    const scope = within(view.container);

    expect(scope.getByRole("option", { name: "Contrato padrão" })).toBeInTheDocument();
    expect(scope.getByRole("option", { name: "Contrato assinado" })).toBeInTheDocument();
  });

  it("disables inputs and shows a busy label while submitting", () => {
    const view = render(<UploadForm onSubmit={vi.fn()} isSubmitting />);
    const scope = within(view.container);

    expect(scope.getByLabelText("Titulo do contrato")).toBeDisabled();
    expect(scope.getByLabelText("Referencia externa")).toBeDisabled();
    expect(scope.getByLabelText("Tipo de contrato")).toBeDisabled();
    expect(scope.getByLabelText("Contrato PDF")).toBeDisabled();
    expect(scope.getByRole("button", { name: "Processando..." })).toBeDisabled();
  });

  it("submits contract metadata and the selected pdf", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const file = new File(["dummy"], "contract.pdf", { type: "application/pdf" });
    const view = render(<UploadForm onSubmit={onSubmit} isSubmitting={false} />);
    const scope = within(view.container);

    await user.type(scope.getByLabelText("Titulo do contrato"), "Loja Centro");
    await user.type(scope.getByLabelText("Referencia externa"), "LOC-001");
    await user.selectOptions(scope.getByLabelText("Tipo de contrato"), "third_party_draft");
    await user.upload(scope.getByLabelText("Contrato PDF"), file);
    await user.click(scope.getByRole("button", { name: "Enviar contrato" }));

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: "Loja Centro",
        externalReference: "LOC-001",
        source: "third_party_draft",
        file,
      }),
    );
  });
});
