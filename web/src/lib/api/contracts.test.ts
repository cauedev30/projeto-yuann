import { afterEach, describe, expect, it, vi } from "vitest";

import {
  getContractDetail,
  getContractSummary,
  getContractVersionDetail,
  listContractVersions,
  updateContract,
  uploadContract,
  uploadContractVersion,
} from "./contracts";

const uploadInput = {
  title: "Loja Centro",
  externalReference: "LOC-001",
  source: "third_party_draft" as const,
  file: new File(["dummy"], "contract.pdf", { type: "application/pdf" }),
};

const versionUploadInput = {
  source: "signed_contract" as const,
  file: new File(["dummy"], "signed-v2.pdf", { type: "application/pdf" }),
};

describe("contracts api client", () => {
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

    await expect(uploadContract(uploadInput, fetchImpl)).rejects.toThrow(
      "O arquivo enviado nao e um PDF legivel.",
    );
  });

  it("falls back to the generic upload error when the response body is unusable", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response("internal-error", {
        status: 500,
      });

    await expect(uploadContract(uploadInput, fetchImpl)).rejects.toThrow(
      "Nao foi possivel enviar o contrato.",
    );
  });

  it("maps canonical contract detail payloads from the API", async () => {
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
            is_active: false,
            activated_at: null,
            last_accessed_at: "2026-03-22T12:00:00Z",
            last_analyzed_at: "2026-03-21T12:00:00Z",
            parties: { tenant: "Loja Centro" },
            financial_terms: { monthly_rent: 12000 },
            field_confidence: {},
          },
          latest_version: {
            contract_version_id: "ver-1",
            version_number: 1,
            created_at: "2026-03-20T12:00:00Z",
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
          events: [],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      );

    const result = await getContractDetail("ctr-1", fetchImpl);

    expect(result.contract.externalReference).toBe("LOC-001");
    expect(result.selectedVersion?.versionNumber).toBe(1);
    expect(result.latestVersion?.originalFilename).toBe("contract.pdf");
    expect(result.selectedAnalysis?.findings[0].clauseName).toBe("Prazo de vigencia");
    expect(result.isHistoricalView).toBe(false);
  });

  it("maps historical contract version detail payloads from the API", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response(
        JSON.stringify({
          contract: {
            id: "ctr-1",
            title: "Loja Centro",
            external_reference: "LOC-001",
            status: "uploaded",
            signature_date: "2026-03-01",
            start_date: "2026-04-01",
            end_date: "2031-03-31",
            term_months: 60,
            is_active: false,
            activated_at: null,
            last_accessed_at: "2026-03-22T12:00:00Z",
            last_analyzed_at: "2026-03-21T12:00:00Z",
            parties: { entities: ["Franquia XPTO LTDA"] },
            financial_terms: { grace_period_months: 3 },
            field_confidence: { term_months: 1 },
          },
          selected_version: {
            contract_version_id: "ver-1",
            version_number: 1,
            created_at: "2026-03-20T12:00:00Z",
            source: "signed_contract",
            original_filename: "signed-v1.pdf",
            used_ocr: false,
            text: "Texto da versao 1",
          },
          latest_version: {
            contract_version_id: "ver-2",
            version_number: 2,
            created_at: "2026-03-21T12:00:00Z",
            source: "signed_contract",
            original_filename: "signed-v2.pdf",
            used_ocr: false,
            text: "Texto da versao 2",
          },
          selected_analysis: {
            analysis_id: "ana-1",
            analysis_status: "completed",
            policy_version: "v1",
            contract_risk_score: 80,
            findings: [],
          },
          events: [],
          is_current: false,
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      );

    const result = await getContractVersionDetail("ctr-1", "ver-1", fetchImpl);

    expect(result.selectedVersion?.contractVersionId).toBe("ver-1");
    expect(result.latestVersion?.contractVersionId).toBe("ver-2");
    expect(result.selectedAnalysis?.analysisStatus).toBe("completed");
    expect(result.isHistoricalView).toBe(true);
    expect(result.contract.signatureDate).toBe("2026-03-01");
  });

  it("maps version list payloads from the API", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response(
        JSON.stringify({
          items: [
            {
              contract_version_id: "ver-2",
              version_number: 2,
              created_at: "2026-03-21T12:00:00Z",
              source: "signed_contract",
              original_filename: "signed-v2.pdf",
              used_ocr: false,
              analysis_status: "completed",
              contract_risk_score: 42,
              is_current: true,
            },
            {
              contract_version_id: "ver-1",
              version_number: 1,
              created_at: "2026-03-20T12:00:00Z",
              source: "signed_contract",
              original_filename: "signed-v1.pdf",
              used_ocr: false,
              analysis_status: null,
              contract_risk_score: null,
              is_current: false,
            },
          ],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      );

    const result = await listContractVersions("ctr-1", fetchImpl);

    expect(result.items).toHaveLength(2);
    expect(result.items[0].versionNumber).toBe(2);
    expect(result.items[0].isCurrent).toBe(true);
    expect(result.items[1].analysisStatus).toBeNull();
  });

  it("sends version-aware URLs for list, detail, summary, and upload", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl = vi.fn<typeof fetch>(async () =>
      new Response(
        JSON.stringify({
          contract_id: "ctr-1",
          contract_version_id: "ver-2",
          version_number: 2,
          source: "signed_contract",
          used_ocr: false,
          text: "texto",
          items: [],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    await listContractVersions("ctr-1", fetchImpl);
    await getContractSummary("ctr-1", "ver-1", fetchImpl);
    await uploadContractVersion("ctr-1", versionUploadInput, fetchImpl);

    expect(fetchImpl).toHaveBeenNthCalledWith(
      1,
      "http://127.0.0.1:8000/api/contracts/ctr-1/versions",
      expect.objectContaining({
        headers: expect.any(Object),
        cache: "no-store",
      }),
    );
    expect(fetchImpl).toHaveBeenNthCalledWith(
      2,
      "http://127.0.0.1:8000/api/contracts/ctr-1/summary?version_id=ver-1",
      expect.objectContaining({
        headers: expect.any(Object),
        cache: "no-store",
      }),
    );
    expect(fetchImpl).toHaveBeenNthCalledWith(
      3,
      "http://127.0.0.1:8000/api/contracts/ctr-1/versions",
      expect.objectContaining({
        method: "POST",
        body: expect.any(FormData),
      }),
    );
  });

  it("maps upload responses for both initial and versioned uploads", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response(
        JSON.stringify({
          contract_id: "ctr-1",
          contract_version_id: "ver-2",
          version_number: 2,
          source: "signed_contract",
          used_ocr: false,
          text: "texto",
        }),
        {
          status: 201,
          headers: { "Content-Type": "application/json" },
        },
      );

    const initialResult = await uploadContract(uploadInput, fetchImpl);
    const versionResult = await uploadContractVersion("ctr-1", versionUploadInput, fetchImpl);

    expect(initialResult.versionNumber).toBe(2);
    expect(versionResult.contractVersionId).toBe("ver-2");
  });

  it("sends is_active when updating a contract lifecycle flag", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl = vi.fn<typeof fetch>(async () =>
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
            is_active: true,
            activated_at: "2026-03-10T12:00:00Z",
            last_accessed_at: null,
            last_analyzed_at: null,
            parties: null,
            financial_terms: null,
            field_confidence: {},
          },
          latest_version: null,
          latest_analysis: null,
          events: [],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    await updateContract("ctr-1", { isActive: true }, fetchImpl);

    expect(fetchImpl).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/contracts/ctr-1",
      expect.objectContaining({
        method: "PATCH",
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
        body: JSON.stringify({ is_active: true }),
      }),
    );
  });

  it("falls back to a generic contracts error when list/detail responses are unusable", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://127.0.0.1:8000");
    const fetchImpl: typeof fetch = async () =>
      new Response("internal-error", {
        status: 500,
      });

    await expect(getContractDetail("ctr-1", fetchImpl)).rejects.toThrow(
      "Nao foi possivel carregar o contrato.",
    );
    await expect(getContractVersionDetail("ctr-1", "ver-1", fetchImpl)).rejects.toThrow(
      "Nao foi possivel carregar o contrato.",
    );
  });
});
