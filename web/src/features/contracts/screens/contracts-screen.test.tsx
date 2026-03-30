import React from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { uploadContract } from "../../../lib/api/contracts";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}));

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
    versionNumber: 1,
    source: "third_party_draft" as const,
    usedOcr: false,
    text: "Prazo de vigencia 36 meses",
  };
}

function buildContractsListResult() {
  return {
    items: [
      {
        id: "ctr-1",
        title: "Loja Centro",
        externalReference: "LOC-001",
        status: "uploaded",
        signatureDate: null,
        startDate: null,
        endDate: null,
        termMonths: 36,
        latestAnalysisStatus: "completed",
        latestRiskScore: 80,
        latestVersionSource: "third_party_draft" as const,
        isActive: true,
        activatedAt: null,
        lastAccessedAt: null,
        lastAnalyzedAt: null,
      },
    ],
  };
}

describe("ContractsScreen", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    pushMock.mockReset();
  });

  function getScreenScope() {
    return within(screen.getAllByRole("main").at(-1) as HTMLElement);
  }

  it("shows the guided empty state before any upload", async () => {
    const loadContracts = vi.fn().mockResolvedValue({ items: [] });

    render(<ContractsScreen submitContract={vi.fn()} loadContracts={loadContracts} />);
    const scope = getScreenScope();

    await waitFor(() => expect(loadContracts).toHaveBeenCalledTimes(1));

    expect(scope.getByText("Contratos")).toBeInTheDocument();
    expect(scope.getByText("Analise de contratos")).toBeInTheDocument();
    expect(scope.getByText("Nenhuma triagem foi executada nesta sessao.")).toBeInTheDocument();
    expect(scope.getByText("Navegação")).toBeInTheDocument();
    expect(scope.getByText(/os achados e o resumo em inteligência artificial/i)).toBeInTheDocument();
    expect(scope.getByRole("link", { name: "Abrir Acervo" })).toBeInTheDocument();
  });

  it("shows processing feedback while the upload is pending", async () => {
    const user = userEvent.setup();
    const loadContracts = vi.fn().mockResolvedValue({ items: [] });
    let resolveUpload:
      | ((value: ReturnType<typeof buildUploadResult>) => void)
      | undefined;
    const submitContract = vi.fn(
      () =>
        new Promise<ReturnType<typeof buildUploadResult>>((resolve) => {
          resolveUpload = resolve;
        }),
    );

    render(<ContractsScreen submitContract={submitContract} loadContracts={loadContracts} />);
    const scope = getScreenScope();

    await waitFor(() => expect(loadContracts).toHaveBeenCalledTimes(1));
    await user.click(scope.getByRole("button", { name: "Enviar contrato" }));

    expect(scope.getAllByText("Processando triagem inicial...").length).toBeGreaterThan(0);

    resolveUpload?.(buildUploadResult());
    await waitFor(() =>
      expect(screen.getByText("Triagem inicial concluida")).toBeInTheDocument(),
    );
  });

  it("shows a contextual error and keeps the form available after a failed upload", async () => {
    const user = userEvent.setup();
    const loadContracts = vi.fn().mockResolvedValue({ items: [] });
    const submitContract = vi.fn().mockRejectedValue(new Error("Falha no envio"));

    render(<ContractsScreen submitContract={submitContract} loadContracts={loadContracts} />);
    const scope = getScreenScope();

    await waitFor(() => expect(loadContracts).toHaveBeenCalledTimes(1));
    await user.click(scope.getByRole("button", { name: "Enviar contrato" }));

    expect(await scope.findByRole("alert")).toHaveTextContent("Falha no envio");
    expect(scope.getByRole("button", { name: "Enviar contrato" })).toBeEnabled();
  });

  it("renders the summary before findings and extracted text after success", async () => {
    const user = userEvent.setup();
    const loadContracts = vi.fn().mockResolvedValue({ items: [] });
    const submitContract = vi.fn().mockResolvedValue(buildUploadResult());

    render(<ContractsScreen submitContract={submitContract} loadContracts={loadContracts} />);
    const scope = getScreenScope();

    await waitFor(() => expect(loadContracts).toHaveBeenCalledTimes(1));
    await user.click(scope.getByRole("button", { name: "Enviar contrato" }));

    await waitFor(() =>
      expect(screen.getAllByRole("heading", { name: "Resumo da triagem" }).length).toBeGreaterThan(0),
    );

    const summaryHeading = screen.getAllByRole("heading", { name: "Resumo da triagem" }).at(-1) as HTMLElement;
    const findingsHeading = screen.getAllByRole("heading", { name: "Principais Pontos" }).at(-1) as HTMLElement;
    const aiSummaryHeading = screen.getAllByRole("heading", { name: "Resumo do contrato" }).at(-1) as HTMLElement;

    expect(
      summaryHeading.compareDocumentPosition(findingsHeading) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(
      findingsHeading.compareDocumentPosition(aiSummaryHeading) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(screen.getByText("Contrato padrão analisado na sessao atual.")).toBeInTheDocument();
    expect(screen.queryByText("Score de risco")).not.toBeInTheDocument();
  });

  it("shows the mapped upload error returned by the transport client", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const user = userEvent.setup();
    const loadContracts = vi.fn().mockResolvedValue({ items: [] });
    const fetchImpl: typeof fetch = async () =>
      new Response(JSON.stringify({ detail: "Uploaded file is not a readable PDF" }), {
        status: 422,
        headers: { "Content-Type": "application/json" },
      });

    render(
      <ContractsScreen
        submitContract={(payload) => uploadContract(payload, fetchImpl)}
        loadContracts={loadContracts}
      />,
    );
    const scope = getScreenScope();

    await waitFor(() => expect(loadContracts).toHaveBeenCalledTimes(1));
    await user.click(scope.getByRole("button", { name: "Enviar contrato" }));

    expect(await scope.findByRole("alert")).toHaveTextContent(
      "O arquivo enviado nao e um PDF legivel.",
    );
  });

  it("shows a loading state while the persisted contracts list is loading", () => {
    const loadContracts = vi.fn(
      () =>
        new Promise<ReturnType<typeof buildContractsListResult>>(() => {
          // keep pending
        }),
    );

    render(<ContractsScreen submitContract={vi.fn()} loadContracts={loadContracts} />);
    const scope = getScreenScope();

    expect(scope.getAllByText("Carregando contratos...").length).toBeGreaterThan(0);
  });

  it("refreshes the persisted contracts list after a successful upload", async () => {
    const user = userEvent.setup();
    const loadContracts = vi
      .fn()
      .mockResolvedValueOnce({ items: [] })
      .mockResolvedValue(buildContractsListResult());
    const submitContract = vi.fn().mockResolvedValue(buildUploadResult());

    render(
      <ContractsScreen
        submitContract={submitContract}
        loadContracts={loadContracts}
      />,
    );
    const scope = getScreenScope();

    expect(await scope.findByRole("link", { name: "Abrir Acervo" })).toBeInTheDocument();
    await user.click(scope.getByRole("button", { name: "Enviar contrato" }));

    await waitFor(() => expect(loadContracts).toHaveBeenCalledTimes(2));
  });
});
