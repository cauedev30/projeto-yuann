export type ContractSource = "third_party_draft" | "signed_contract";

export type ContractListItemSummary = {
  id: string;
  title: string;
  externalReference: string;
  status: string;
  signatureDate: string | null;
  startDate: string | null;
  endDate: string | null;
  termMonths: number | null;
  latestAnalysisStatus: string | null;
  latestRiskScore: number | null;
  latestVersionSource: ContractSource | null;
};

export type ContractListResponse = {
  items: ContractListItemSummary[];
};

export type ContractListItemPayload = {
  id: string;
  title: string;
  external_reference: string;
  status: string;
  signature_date: string | null;
  start_date: string | null;
  end_date: string | null;
  term_months: number | null;
  latest_analysis_status: string | null;
  latest_contract_risk_score: number | null;
  latest_version_source: ContractSource | null;
};

export type ContractListResponsePayload = {
  items: ContractListItemPayload[];
};

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
  id?: string;
  clauseName: string;
  status: "critical" | "attention" | "conforme";
  severity?: string;
  riskExplanation: string;
  currentSummary: string;
  policyRule: string;
  suggestedAdjustmentDirection: string;
  metadata?: Record<string, unknown>;
};

export type ContractDetailSummary = {
  id: string;
  title: string;
  externalReference: string;
  status: string;
  signatureDate: string | null;
  startDate: string | null;
  endDate: string | null;
  termMonths: number | null;
  parties: Record<string, unknown> | null;
  financialTerms: Record<string, unknown> | null;
};

export type ContractVersionSummary = {
  contractVersionId: string;
  source: ContractSource;
  originalFilename: string;
  usedOcr: boolean;
  text: string | null;
};

export type ContractLatestAnalysisSummary = {
  analysisId: string;
  analysisStatus: string;
  policyVersion: string;
  contractRiskScore: number | null;
  findings: ContractFinding[];
};

export type ContractDetail = {
  contract: ContractDetailSummary;
  latestVersion: ContractVersionSummary | null;
  latestAnalysis: ContractLatestAnalysisSummary | null;
};

export type ContractDetailSummaryPayload = {
  id: string;
  title: string;
  external_reference: string;
  status: string;
  signature_date: string | null;
  start_date: string | null;
  end_date: string | null;
  term_months: number | null;
  parties: Record<string, unknown> | null;
  financial_terms: Record<string, unknown> | null;
};

export type ContractVersionSummaryPayload = {
  contract_version_id: string;
  source: ContractSource;
  original_filename: string;
  used_ocr: boolean;
  text: string | null;
};

export type ContractAnalysisFindingSummaryPayload = {
  id: string;
  clause_name: string;
  status: ContractFinding["status"];
  severity: string;
  current_summary: string;
  policy_rule: string;
  risk_explanation: string;
  suggested_adjustment_direction: string;
  metadata: Record<string, unknown>;
};

export type ContractLatestAnalysisSummaryPayload = {
  analysis_id: string;
  analysis_status: string;
  policy_version: string;
  contract_risk_score: number | null;
  findings: ContractAnalysisFindingSummaryPayload[];
};

export type ContractDetailResponsePayload = {
  contract: ContractDetailSummaryPayload;
  latest_version: ContractVersionSummaryPayload | null;
  latest_analysis: ContractLatestAnalysisSummaryPayload | null;
};

function mapContractFinding(
  payload: ContractAnalysisFindingSummaryPayload,
): ContractFinding {
  return {
    id: payload.id,
    clauseName: payload.clause_name,
    status: payload.status,
    severity: payload.severity,
    currentSummary: payload.current_summary,
    policyRule: payload.policy_rule,
    riskExplanation: payload.risk_explanation,
    suggestedAdjustmentDirection: payload.suggested_adjustment_direction,
    metadata: payload.metadata,
  };
}

export function mapContractListResponse(
  payload: ContractListResponsePayload,
): ContractListResponse {
  return {
    items: payload.items.map((item) => ({
      id: item.id,
      title: item.title,
      externalReference: item.external_reference,
      status: item.status,
      signatureDate: item.signature_date,
      startDate: item.start_date,
      endDate: item.end_date,
      termMonths: item.term_months,
      latestAnalysisStatus: item.latest_analysis_status,
      latestRiskScore: item.latest_contract_risk_score,
      latestVersionSource: item.latest_version_source,
    })),
  };
}

export function mapContractDetailResponse(
  payload: ContractDetailResponsePayload,
): ContractDetail {
  return {
    contract: {
      id: payload.contract.id,
      title: payload.contract.title,
      externalReference: payload.contract.external_reference,
      status: payload.contract.status,
      signatureDate: payload.contract.signature_date,
      startDate: payload.contract.start_date,
      endDate: payload.contract.end_date,
      termMonths: payload.contract.term_months,
      parties: payload.contract.parties,
      financialTerms: payload.contract.financial_terms,
    },
    latestVersion: payload.latest_version
      ? {
          contractVersionId: payload.latest_version.contract_version_id,
          source: payload.latest_version.source,
          originalFilename: payload.latest_version.original_filename,
          usedOcr: payload.latest_version.used_ocr,
          text: payload.latest_version.text,
        }
      : null,
    latestAnalysis: payload.latest_analysis
      ? {
          analysisId: payload.latest_analysis.analysis_id,
          analysisStatus: payload.latest_analysis.analysis_status,
          policyVersion: payload.latest_analysis.policy_version,
          contractRiskScore: payload.latest_analysis.contract_risk_score,
          findings: payload.latest_analysis.findings.map(mapContractFinding),
        }
      : null,
  };
}

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
