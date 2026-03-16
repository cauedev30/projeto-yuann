export type ContractSource = "third_party_draft" | "signed_contract";

export type ContractUploadInput = {
  title: string;
  externalReference: string;
  source: ContractSource;
  file: File;
};

export type ContractUploadResult = {
  contractId: string;
  contractVersionId: string;
  source: ContractSource;
  usedOcr: boolean;
  text: string;
};

export type ContractUploadResponsePayload = {
  contract_id: string;
  contract_version_id: string;
  source: ContractSource;
  used_ocr: boolean;
  text: string;
};

export type ContractFinding = {
  clauseName: string;
  status: "critical" | "attention" | "conforme";
  riskExplanation: string;
  currentSummary: string;
  policyRule: string;
  suggestedAdjustmentDirection: string;
};

export function mapUploadResponseToContractUploadResult(
  payload: ContractUploadResponsePayload,
): ContractUploadResult {
  return {
    contractId: payload.contract_id,
    contractVersionId: payload.contract_version_id,
    source: payload.source,
    usedOcr: payload.used_ocr,
    text: payload.text,
  };
}
