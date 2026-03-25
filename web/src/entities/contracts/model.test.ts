import { describe, expect, it } from "vitest";

import {
  mapContractDetailResponse,
  mapContractListResponse,
  mapUploadResponseToContractUploadResult,
} from "./model";

describe("contracts entity mapping", () => {
  it("maps snake_case upload payloads into UI-facing contract upload results", () => {
    const result = mapUploadResponseToContractUploadResult({
      contract_id: "ctr-1",
      contract_version_id: "ver-1",
      source: "third_party_draft",
      used_ocr: false,
      text: "Prazo de vigencia 60 meses",
    });

    expect(result.contractId).toBe("ctr-1");
    expect(result.usedOcr).toBe(false);
  });

  it("maps contract list payloads into UI-facing summaries", () => {
    const result = mapContractListResponse({
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
          is_active: true,
          activated_at: "2026-03-10T12:00:00Z",
          last_accessed_at: "2026-03-20T12:00:00Z",
          last_analyzed_at: "2026-03-18T12:00:00Z",
          latest_analysis_status: "completed",
          latest_contract_risk_score: 80,
          latest_version_source: "third_party_draft",
        },
      ],
    });

    expect(result.items[0].externalReference).toBe("LOC-001");
    expect(result.items[0].latestRiskScore).toBe(80);
    expect(result.items[0].latestVersionSource).toBe("third_party_draft");
    expect(result.items[0].isActive).toBe(true);
    expect(result.items[0].activatedAt).toBe("2026-03-10T12:00:00Z");
    expect(result.items[0].lastAccessedAt).toBe("2026-03-20T12:00:00Z");
    expect(result.items[0].lastAnalyzedAt).toBe("2026-03-18T12:00:00Z");
  });

  it("maps contract detail payloads and preserves null derived sections", () => {
    const result = mapContractDetailResponse({
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
        parties: null,
        financial_terms: null,
        field_confidence: {},
      },
      latest_version: null,
      latest_analysis: null,
      events: [],
    });

    expect(result.contract.externalReference).toBe("LOC-001");
    expect(result.contract.termMonths).toBe(36);
    expect(result.contract.isActive).toBe(false);
    expect(result.contract.lastAccessedAt).toBe("2026-03-22T12:00:00Z");
    expect(result.contract.lastAnalyzedAt).toBe("2026-03-21T12:00:00Z");
    expect(result.latestVersion).toBeNull();
    expect(result.latestAnalysis).toBeNull();
  });
});
