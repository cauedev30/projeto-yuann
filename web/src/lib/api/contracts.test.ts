import { afterEach, describe, expect, it, vi } from "vitest";

import { getContractDetail, listContracts, uploadContract } from "./contracts";

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

  it("maps list contracts payloads from the API", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response(
        JSON.stringify({
          items: [
            {
              id: "ctr-1",
              title: "Loja Centro",
              external_reference: "LOC-001",
              status: "uploaded",
              signature_date: null,
              start_date: null,
              end_date: null,
              term_months: 36,
              latest_analysis_status: "completed",
              latest_contract_risk_score: 80,
              latest_version_source: "third_party_draft",
            },
          ],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      );

    const result = await listContracts(fetchImpl);

    expect(result.items[0].title).toBe("Loja Centro");
    expect(result.items[0].latestRiskScore).toBe(80);
  });

  it("maps contract detail payloads from the API", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response(
        JSON.stringify({
          contract: {
            id: "ctr-1",
            title: "Loja Centro",
            external_reference: "LOC-001",
            status: "uploaded",
            signature_date: null,
            start_date: null,
            end_date: null,
            term_months: 36,
            parties: { tenant: "Loja Centro" },
            financial_terms: { monthly_rent: 12000 },
          },
          latest_version: {
            contract_version_id: "ver-1",
            source: "third_party_draft",
            original_filename: "contract.pdf",
            used_ocr: false,
            text: "Prazo de vigencia 36 meses",
          },
          latest_analysis: {
            analysis_id: "ana-1",
            analysis_status: "completed",
            policy_version: "v1",
            contract_risk_score: 80,
            findings: [
              {
                id: "finding-1",
                clause_name: "Prazo de vigencia",
                status: "critical",
                severity: "critical",
                current_summary: "Prazo atual de 36 meses.",
                policy_rule: "Prazo minimo exigido: 60 meses.",
                risk_explanation: "Prazo abaixo do minimo permitido pela politica.",
                suggested_adjustment_direction: "Solicitar prazo minimo de 60 meses.",
                metadata: {},
              },
            ],
          },
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      );

    const result = await getContractDetail("ctr-1", fetchImpl);

    expect(result.contract.externalReference).toBe("LOC-001");
    expect(result.latestVersion?.originalFilename).toBe("contract.pdf");
    expect(result.latestAnalysis?.findings[0].clauseName).toBe("Prazo de vigencia");
  });

  it("falls back to a generic contracts error when list/detail responses are unusable", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response("internal-error", {
        status: 500,
      });

    await expect(listContracts(fetchImpl)).rejects.toThrow(
      "Nao foi possivel carregar os contratos.",
    );
    await expect(getContractDetail("ctr-1", fetchImpl)).rejects.toThrow(
      "Nao foi possivel carregar o contrato.",
    );
  });
});
