import { describe, expect, it } from "vitest";

import { mapUploadResponseToContractUploadResult } from "./model";

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
});
