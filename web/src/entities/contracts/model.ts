export type ContractSource = "third_party_draft" | "signed_contract";
export type ContractScope = "all" | "active" | "history";

export type ContractEventType =
  | "renewal"
  | "expiration"
  | "readjustment"
  | "grace_period_end";

export type ContractEventSummary = {
  id: string;
  eventType: ContractEventType;
  eventDate: string | null;
  leadTimeDays: number;
  metadata: Record<string, unknown>;
};

export type ContractEventSummaryPayload = {
  id: string;
  event_type: string;
  event_date: string | null;
  lead_time_days: number;
  metadata: Record<string, unknown>;
};

export type ContractListItemSummary = {
  id: string;
  title: string;
  externalReference: string;
  status: string;
  signatureDate: string | null;
  startDate: string | null;
  endDate: string | null;
  termMonths: number | null;
  isActive: boolean;
  activatedAt: string | null;
  lastAccessedAt: string | null;
  lastAnalyzedAt: string | null;
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
  is_active: boolean;
  activated_at: string | null;
  last_accessed_at: string | null;
  last_analyzed_at: string | null;
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

export type ContractVersionUploadInput = {
  source: ContractSource;
  file: File;
};

export type ContractUploadResult = {
  contractId: string;
  contractVersionId: string;
  versionNumber: number;
  source: ContractSource;
  usedOcr: boolean;
  text: string;
};

export type ContractUploadResponsePayload = {
  contract_id: string;
  contract_version_id: string;
  version_number: number;
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
  isActive: boolean;
  activatedAt: string | null;
  lastAccessedAt: string | null;
  lastAnalyzedAt: string | null;
  parties: Record<string, unknown> | null;
  financialTerms: Record<string, unknown> | null;
  fieldConfidence: Record<string, number>;
};

export type ContractVersionSummary = {
  contractVersionId: string;
  versionNumber: number;
  createdAt: string;
  source: ContractSource;
  originalFilename: string;
  usedOcr: boolean;
  text: string | null;
};

export type ContractVersionListItem = {
  contractVersionId: string;
  versionNumber: number;
  createdAt: string;
  source: ContractSource;
  originalFilename: string;
  usedOcr: boolean;
  analysisStatus: string | null;
  contractRiskScore: number | null;
  isCurrent: boolean;
};

export type ContractVersionListResponse = {
  items: ContractVersionListItem[];
};

export type ContractVersionTextDiffLine = {
  kind: "added" | "removed" | "unchanged";
  value: string;
};

export type ContractVersionTextDiff = {
  hasChanges: boolean;
  lines: ContractVersionTextDiffLine[];
};

export type ContractFindingDiffItem = {
  clauseName: string;
  changeType: "added" | "removed" | "changed";
  previousStatus: string | null;
  currentStatus: string | null;
  previousSummary: string | null;
  currentSummary: string | null;
};

export type ContractFindingsDiff = {
  items: ContractFindingDiffItem[];
};

export type ContractVersionComparison = {
  selectedVersion: ContractVersionSummary;
  baselineVersion: ContractVersionSummary | null;
  summary: string;
  textDiff: ContractVersionTextDiff;
  findingsDiff: ContractFindingsDiff;
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
  selectedVersion: ContractVersionSummary | null;
  latestVersion: ContractVersionSummary | null;
  selectedAnalysis: ContractLatestAnalysisSummary | null;
  events: ContractEventSummary[];
  isCurrent: boolean;
  isHistoricalView: boolean;
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
  is_active: boolean;
  activated_at: string | null;
  last_accessed_at: string | null;
  last_analyzed_at: string | null;
  parties: Record<string, unknown> | null;
  financial_terms: Record<string, unknown> | null;
  field_confidence: Record<string, number>;
};

export type ContractVersionSummaryPayload = {
  contract_version_id: string;
  version_number: number;
  created_at: string;
  source: ContractSource;
  original_filename: string;
  used_ocr: boolean;
  text: string | null;
};

export type ContractVersionListItemPayload = {
  contract_version_id: string;
  version_number: number;
  created_at: string;
  source: ContractSource;
  original_filename: string;
  used_ocr: boolean;
  analysis_status: string | null;
  contract_risk_score: number | null;
  is_current: boolean;
};

export type ContractVersionListResponsePayload = {
  items: ContractVersionListItemPayload[];
};

export type ContractVersionTextDiffLinePayload = {
  kind: ContractVersionTextDiffLine["kind"];
  value: string;
};

export type ContractVersionTextDiffPayload = {
  has_changes: boolean;
  lines: ContractVersionTextDiffLinePayload[];
};

export type ContractFindingDiffItemPayload = {
  clause_name: string;
  change_type: ContractFindingDiffItem["changeType"];
  previous_status: string | null;
  current_status: string | null;
  previous_summary: string | null;
  current_summary: string | null;
};

export type ContractFindingsDiffPayload = {
  items: ContractFindingDiffItemPayload[];
};

export type ContractVersionComparisonResponsePayload = {
  selected_version: ContractVersionSummaryPayload;
  baseline_version: ContractVersionSummaryPayload | null;
  summary: string;
  text_diff: ContractVersionTextDiffPayload;
  findings_diff: ContractFindingsDiffPayload;
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
  events: ContractEventSummaryPayload[];
};

export type ContractVersionDetailResponsePayload = {
  contract: ContractDetailSummaryPayload;
  selected_version: ContractVersionSummaryPayload | null;
  latest_version: ContractVersionSummaryPayload | null;
  selected_analysis: ContractLatestAnalysisSummaryPayload | null;
  events: ContractEventSummaryPayload[];
  is_current: boolean;
};

function mapContractEvent(payload: ContractEventSummaryPayload): ContractEventSummary {
  return {
    id: payload.id,
    eventType: payload.event_type as ContractEventType,
    eventDate: payload.event_date,
    leadTimeDays: payload.lead_time_days,
    metadata: payload.metadata,
  };
}

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

function mapContractSummary(
  payload: ContractDetailSummaryPayload,
): ContractDetailSummary {
  return {
    id: payload.id,
    title: payload.title,
    externalReference: payload.external_reference,
    status: payload.status,
    signatureDate: payload.signature_date,
    startDate: payload.start_date,
    endDate: payload.end_date,
    termMonths: payload.term_months,
    isActive: payload.is_active,
    activatedAt: payload.activated_at,
    lastAccessedAt: payload.last_accessed_at,
    lastAnalyzedAt: payload.last_analyzed_at,
    parties: payload.parties,
    financialTerms: payload.financial_terms,
    fieldConfidence: payload.field_confidence,
  };
}

function mapContractVersionSummary(
  payload: ContractVersionSummaryPayload | null,
): ContractVersionSummary | null {
  if (!payload) {
    return null;
  }

  return {
    contractVersionId: payload.contract_version_id,
    versionNumber: payload.version_number,
    createdAt: payload.created_at,
    source: payload.source,
    originalFilename: payload.original_filename,
    usedOcr: payload.used_ocr,
    text: payload.text,
  };
}

function mapContractAnalysisSummary(
  payload: ContractLatestAnalysisSummaryPayload | null,
): ContractLatestAnalysisSummary | null {
  if (!payload) {
    return null;
  }

  return {
    analysisId: payload.analysis_id,
    analysisStatus: payload.analysis_status,
    policyVersion: payload.policy_version,
    contractRiskScore: payload.contract_risk_score,
    findings: payload.findings.map(mapContractFinding),
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
      isActive: item.is_active,
      activatedAt: item.activated_at,
      lastAccessedAt: item.last_accessed_at,
      lastAnalyzedAt: item.last_analyzed_at,
      latestAnalysisStatus: item.latest_analysis_status,
      latestRiskScore: item.latest_contract_risk_score,
      latestVersionSource: item.latest_version_source,
    })),
  };
}

export function mapContractDetailResponse(
  payload: ContractDetailResponsePayload,
): ContractDetail {
  const latestVersion = mapContractVersionSummary(payload.latest_version);
  const selectedAnalysis = mapContractAnalysisSummary(payload.latest_analysis);

  return {
    contract: mapContractSummary(payload.contract),
    selectedVersion: latestVersion,
    latestVersion,
    selectedAnalysis,
    events: payload.events.map(mapContractEvent),
    isCurrent: true,
    isHistoricalView: false,
  };
}

export function mapContractVersionDetailResponse(
  payload: ContractVersionDetailResponsePayload,
): ContractDetail {
  return {
    contract: mapContractSummary(payload.contract),
    selectedVersion: mapContractVersionSummary(payload.selected_version),
    latestVersion: mapContractVersionSummary(payload.latest_version),
    selectedAnalysis: mapContractAnalysisSummary(payload.selected_analysis),
    events: payload.events.map(mapContractEvent),
    isCurrent: payload.is_current,
    isHistoricalView: !payload.is_current,
  };
}

export function mapContractVersionListResponse(
  payload: ContractVersionListResponsePayload,
): ContractVersionListResponse {
  return {
    items: payload.items.map((item) => ({
      contractVersionId: item.contract_version_id,
      versionNumber: item.version_number,
      createdAt: item.created_at,
      source: item.source,
      originalFilename: item.original_filename,
      usedOcr: item.used_ocr,
      analysisStatus: item.analysis_status,
      contractRiskScore: item.contract_risk_score,
      isCurrent: item.is_current,
    })),
  };
}

export function mapContractVersionComparisonResponse(
  payload: ContractVersionComparisonResponsePayload,
): ContractVersionComparison {
  return {
    selectedVersion: mapContractVersionSummary(payload.selected_version)!,
    baselineVersion: mapContractVersionSummary(payload.baseline_version),
    summary: payload.summary,
    textDiff: {
      hasChanges: payload.text_diff.has_changes,
      lines: payload.text_diff.lines.map((line) => ({
        kind: line.kind,
        value: line.value,
      })),
    },
    findingsDiff: {
      items: payload.findings_diff.items.map((item) => ({
        clauseName: item.clause_name,
        changeType: item.change_type,
        previousStatus: item.previous_status,
        currentStatus: item.current_status,
        previousSummary: item.previous_summary,
        currentSummary: item.current_summary,
      })),
    },
  };
}

export function mapUploadResponseToContractUploadResult(
  payload: ContractUploadResponsePayload,
): ContractUploadResult {
  return {
    contractId: payload.contract_id,
    contractVersionId: payload.contract_version_id,
    versionNumber: payload.version_number,
    source: payload.source,
    usedOcr: payload.used_ocr,
    text: payload.text,
  };
}
