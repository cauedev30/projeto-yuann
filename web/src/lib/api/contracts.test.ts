import { afterEach, describe, expect, it, vi } from "vitest";

import { uploadContract } from "./contracts";

const input = {
  title: "Loja Centro",
  externalReference: "LOC-001",
  source: "third_party_draft" as const,
  file: new File(["dummy"], "contract.pdf", { type: "application/pdf" }),
};

describe("uploadContract", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("maps an unreadable-pdf backend error into Portuguese copy", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response(JSON.stringify({ detail: "Uploaded file is not a readable PDF" }), {
        status: 422,
        headers: { "Content-Type": "application/json" },
      });

    await expect(uploadContract(input, fetchImpl)).rejects.toThrow(
      "O arquivo enviado nao e um PDF legivel.",
    );
  });

  it("falls back to the generic upload error when the response body is unusable", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response("internal-error", {
        status: 500,
      });

    await expect(uploadContract(input, fetchImpl)).rejects.toThrow(
      "Nao foi possivel enviar o contrato.",
    );
  });
});
