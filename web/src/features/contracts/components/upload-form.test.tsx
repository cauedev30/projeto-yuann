import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { UploadForm } from "./upload-form";


describe("UploadForm", () => {
  it("submits contract metadata and the selected pdf", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    const file = new File(["dummy"], "contract.pdf", { type: "application/pdf" });

    render(<UploadForm onSubmit={onSubmit} isSubmitting={false} />);

    await user.type(screen.getByLabelText("Titulo do contrato"), "Loja Centro");
    await user.type(screen.getByLabelText("Referencia externa"), "LOC-001");
    await user.selectOptions(screen.getByLabelText("Tipo de contrato"), "third_party_draft");
    await user.upload(screen.getByLabelText("Contrato PDF"), file);
    await user.click(screen.getByRole("button", { name: "Enviar contrato" }));

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
