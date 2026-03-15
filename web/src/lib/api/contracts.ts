import { getClientEnv } from "@/lib/env";

export type ContractSource = "third_party_draft" | "signed_contract";

export type ContractUploadInput = {
  title: string;
  externalReference: string;
  source: ContractSource;
  file: File;
};

export type ContractUploadResponse = {
  contractId: string;
  contractVersionId: string;
  source: ContractSource;
  usedOcr: boolean;
  text: string;
};

export type FindingItem = {
  clauseName: string;
  status: "critical" | "attention" | "conforme";
  riskExplanation: string;
  currentSummary: string;
  policyRule: string;
  suggestedAdjustmentDirection: string;
};

export async function uploadContract(
  input: ContractUploadInput,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractUploadResponse> {
  const formData = new FormData();
  formData.set("title", input.title);
  formData.set("external_reference", input.externalReference);
  formData.set("source", input.source);
  formData.set("file", input.file);

  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/uploads/contracts`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Nao foi possivel enviar o contrato.");
  }

  const payload = (await response.json()) as {
    contract_id: string;
    contract_version_id: string;
    source: ContractSource;
    used_ocr: boolean;
    text: string;
  };

  return {
    contractId: payload.contract_id,
    contractVersionId: payload.contract_version_id,
    source: payload.source,
    usedOcr: payload.used_ocr,
    text: payload.text,
  };
}
