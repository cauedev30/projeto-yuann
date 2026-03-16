import React from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

vi.mock("../components/upload-form", () => ({
  UploadForm: ({
    onSubmit,
    isSubmitting,
  }: {
    onSubmit: (payload: {
      title: string;
      externalReference: string;
      source: "third_party_draft";
      file: File;
    }) => Promise<void> | void;
    isSubmitting: boolean;
  }) => (
    <button
      disabled={isSubmitting}
      onClick={() =>
        onSubmit({
          title: "Loja Centro",
          externalReference: "LOC-001",
          source: "third_party_draft",
          file: new File(["dummy"], "contract.pdf", { type: "application/pdf" }),
        })
      }
      type="button"
    >
      {isSubmitting ? "Processando envio" : "Enviar contrato"}
    </button>
  ),
}));

import { ContractsScreen } from "./contracts-screen";

function buildUploadResult() {
  return {
    contractId: "contract-1",
    contractVersionId: "version-1",
    source: "third_party_draft" as const,
    usedOcr: false,
    text: "Prazo de vigencia 36 meses",
  };
}

describe("ContractsScreen", () => {
  function getScreenScope() {
    return within(screen.getAllByRole("main").at(-1) as HTMLElement);
  }

  it("shows the guided empty state before any upload", () => {
    render(<ContractsScreen submitContract={vi.fn()} />);
    const scope = getScreenScope();

    expect(scope.getByText("Envie um contrato para triagem inicial")).toBeInTheDocument();
    expect(scope.getByText("Nenhuma triagem foi executada nesta sessao.")).toBeInTheDocument();
  });

  it("shows processing feedback while the upload is pending", async () => {
    const user = userEvent.setup();
    let resolveUpload:
      | ((value: ReturnType<typeof buildUploadResult>) => void)
      | undefined;
    const submitContract = vi.fn(
      () =>
        new Promise<ReturnType<typeof buildUploadResult>>((resolve) => {
          resolveUpload = resolve;
        }),
    );

    render(<ContractsScreen submitContract={submitContract} />);
    const scope = getScreenScope();

    await user.click(scope.getByRole("button", { name: "Enviar contrato" }));

    expect(scope.getByText("Processando triagem inicial...")).toBeInTheDocument();

    resolveUpload?.(buildUploadResult());
    await waitFor(() =>
      expect(screen.getByText("Triagem inicial concluida")).toBeInTheDocument(),
    );
  });

  it("shows a contextual error and keeps the form available after a failed upload", async () => {
    const user = userEvent.setup();
    const submitContract = vi.fn().mockRejectedValue(new Error("Falha no envio"));

    render(<ContractsScreen submitContract={submitContract} />);
    const scope = getScreenScope();

    await user.click(scope.getByRole("button", { name: "Enviar contrato" }));

    expect(await scope.findByRole("alert")).toHaveTextContent("Falha no envio");
    expect(scope.getByRole("button", { name: "Enviar contrato" })).toBeEnabled();
  });

  it("renders the summary before findings and extracted text after success", async () => {
    const user = userEvent.setup();
    const submitContract = vi.fn().mockResolvedValue(buildUploadResult());

    render(<ContractsScreen submitContract={submitContract} />);
    const scope = getScreenScope();

    await user.click(scope.getByRole("button", { name: "Enviar contrato" }));

    await waitFor(() =>
      expect(screen.getAllByRole("heading", { name: "Resumo da triagem" }).length).toBeGreaterThan(0),
    );

    const summaryHeading = screen.getAllByRole("heading", { name: "Resumo da triagem" }).at(-1) as HTMLElement;
    const findingsHeading = screen.getAllByRole("heading", { name: "Findings principais" }).at(-1) as HTMLElement;
    const extractedTextHeading = screen.getAllByRole("heading", { name: "Texto extraido" }).at(-1) as HTMLElement;

    expect(
      summaryHeading.compareDocumentPosition(findingsHeading) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(
      findingsHeading.compareDocumentPosition(extractedTextHeading) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });
});
