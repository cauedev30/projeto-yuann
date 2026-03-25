import { getAuthHeaders } from "./auth";
import { getClientEnv } from "../env";
import {
  type ContractVersionComparison,
  type ContractVersionComparisonResponsePayload,
  type ContractDetail,
  type ContractDetailResponsePayload,
  type ContractListResponse,
  type ContractListResponsePayload,
  type ContractScope,
  type ContractUploadInput,
  type ContractUploadResponsePayload,
  type ContractUploadResult,
  type ContractVersionDetailResponsePayload,
  type ContractVersionListResponse,
  type ContractVersionListResponsePayload,
  type ContractVersionUploadInput,
  mapContractDetailResponse,
  mapContractListResponse,
  mapContractVersionComparisonResponse,
  mapContractVersionDetailResponse,
  mapContractVersionListResponse,
  mapUploadResponseToContractUploadResult,
} from "../../entities/contracts/model";

export type ContractSummaryResponse = {
  summary: string;
  key_points: string[];
};

const GENERIC_UPLOAD_ERROR = "Nao foi possivel enviar o contrato.";
const GENERIC_LIST_ERROR = "Nao foi possivel carregar os contratos.";
const GENERIC_DETAIL_ERROR = "Nao foi possivel carregar o contrato.";

export class ContractsApiError extends Error {
  constructor(
    message: string,
    readonly statusCode?: number,
  ) {
    super(message);
    this.name = "ContractsApiError";
  }
}

function mapUploadErrorDetail(detail: unknown): string | null {
  if (detail === "Uploaded file is not a readable PDF") {
    return "O arquivo enviado nao e um PDF legivel.";
  }

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  return null;
}

function mapStringDetail(detail: unknown): string | null {
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  return null;
}

async function buildApiError(
  response: Response,
  genericMessage: string,
  detailMapper: (detail: unknown) => string | null = mapStringDetail,
): Promise<ContractsApiError> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    return new ContractsApiError(
      detailMapper(payload.detail) ?? genericMessage,
      response.status,
    );
  } catch {
    return new ContractsApiError(genericMessage, response.status);
  }
}

export async function uploadContract(
  input: ContractUploadInput,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractUploadResult> {
  const formData = new FormData();
  formData.set("title", input.title);
  formData.set("external_reference", input.externalReference);
  formData.set("source", input.source);
  formData.set("file", input.file);

  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/uploads/contracts`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    throw await buildApiError(response, GENERIC_UPLOAD_ERROR, mapUploadErrorDetail);
  }

  const payload = (await response.json()) as ContractUploadResponsePayload;
  return mapUploadResponseToContractUploadResult(payload);
}

export async function uploadContractVersion(
  contractId: string,
  input: ContractVersionUploadInput,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractUploadResult> {
  const formData = new FormData();
  formData.set("source", input.source);
  formData.set("file", input.file);

  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}/versions`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    throw await buildApiError(response, GENERIC_UPLOAD_ERROR, mapUploadErrorDetail);
  }

  const payload = (await response.json()) as ContractUploadResponsePayload;
  return mapUploadResponseToContractUploadResult(payload);
}

export async function listContracts(
  scopeOrFetchImpl?: ContractScope | typeof fetch,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractListResponse> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const scope =
    typeof scopeOrFetchImpl === "function" || scopeOrFetchImpl === undefined
      ? undefined
      : scopeOrFetchImpl;
  const resolvedFetchImpl =
    typeof scopeOrFetchImpl === "function" ? scopeOrFetchImpl : fetchImpl;
  const url = new URL(`${NEXT_PUBLIC_API_URL}/api/contracts`);
  if (scope !== undefined) {
    url.searchParams.set("scope", scope);
  }

  const response = await resolvedFetchImpl(url.toString(), {
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw await buildApiError(response, GENERIC_LIST_ERROR);
  }

  const payload = (await response.json()) as ContractListResponsePayload;
  return mapContractListResponse(payload);
}

export async function listContractVersions(
  contractId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractVersionListResponse> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}/versions`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw await buildApiError(response, GENERIC_DETAIL_ERROR);
  }

  const payload = (await response.json()) as ContractVersionListResponsePayload;
  return mapContractVersionListResponse(payload);
}

export async function compareContractVersions(
  contractId: string,
  input: {
    selectedVersionId?: string;
    baselineVersionId?: string | null;
  },
  fetchImpl: typeof fetch = fetch,
): Promise<ContractVersionComparison> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const url = new URL(`${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}/compare`);
  if (input.selectedVersionId) {
    url.searchParams.set("selected_version_id", input.selectedVersionId);
  }
  if (input.baselineVersionId) {
    url.searchParams.set("baseline_version_id", input.baselineVersionId);
  }

  const response = await fetchImpl(url.toString(), {
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw await buildApiError(response, "Nao foi possivel comparar as versoes do contrato.");
  }

  const payload = (await response.json()) as ContractVersionComparisonResponsePayload;
  return mapContractVersionComparisonResponse(payload);
}

export async function getContractDetail(
  contractId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractDetail> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw await buildApiError(response, GENERIC_DETAIL_ERROR);
  }

  const payload = (await response.json()) as ContractDetailResponsePayload;
  return mapContractDetailResponse(payload);
}

export async function getContractVersionDetail(
  contractId: string,
  versionId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractDetail> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(
    `${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}/versions/${versionId}`,
    {
      headers: getAuthHeaders(),
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw await buildApiError(response, GENERIC_DETAIL_ERROR);
  }

  const payload = (await response.json()) as ContractVersionDetailResponsePayload;
  return mapContractVersionDetailResponse(payload);
}

export async function deleteContract(
  contractId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<void> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw await buildApiError(response, "Nao foi possivel apagar o contrato.");
  }
}

export async function updateContract(
  contractId: string,
  updates: {
    title?: string;
    signatureDate?: string | null;
    startDate?: string | null;
    endDate?: string | null;
    termMonths?: number | null;
    isActive?: boolean;
  },
  fetchImpl: typeof fetch = fetch,
): Promise<ContractDetail> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();

  const payload: Record<string, unknown> = {};
  if (updates.title !== undefined) payload.title = updates.title;
  if (updates.signatureDate !== undefined) payload.signature_date = updates.signatureDate;
  if (updates.startDate !== undefined) payload.start_date = updates.startDate;
  if (updates.endDate !== undefined) payload.end_date = updates.endDate;
  if (updates.termMonths !== undefined) payload.term_months = updates.termMonths;
  if (updates.isActive !== undefined) payload.is_active = updates.isActive;

  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw await buildApiError(response, "Nao foi possivel atualizar o contrato.");
  }

  const responsePayload = (await response.json()) as ContractDetailResponsePayload;
  return mapContractDetailResponse(responsePayload);
}

export async function getContractSummary(
  contractId: string,
  versionIdOrFetchImpl?: string | typeof fetch,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractSummaryResponse> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const versionId =
    typeof versionIdOrFetchImpl === "function" || versionIdOrFetchImpl === undefined
      ? undefined
      : versionIdOrFetchImpl;
  const resolvedFetchImpl =
    typeof versionIdOrFetchImpl === "function" ? versionIdOrFetchImpl : fetchImpl;
  const url = new URL(`${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}/summary`);
  if (versionId !== undefined) {
    url.searchParams.set("version_id", versionId);
  }

  const response = await resolvedFetchImpl(url.toString(), {
    headers: getAuthHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw await buildApiError(response, "Nao foi possivel gerar o resumo do contrato.");
  }

  return (await response.json()) as ContractSummaryResponse;
}

export type CorrectionItem = {
  clause_name: string;
  original_text: string;
  corrected_text: string;
  reason: string;
};

export type CorrectedContractResponse = {
  corrected_text: string;
  corrections: CorrectionItem[];
};

export async function analyzeContract(
  contractId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractDetail> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(
    `${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}/analyze`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    },
  );

  if (!response.ok) {
    throw await buildApiError(response, "Nao foi possivel analisar o contrato.");
  }

  const payload = (await response.json()) as ContractDetailResponsePayload;
  return mapContractDetailResponse(payload);
}

export async function generateCorrectedContract(
  contractId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<CorrectedContractResponse> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(
    `${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}/generate-corrected`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    },
  );

  if (!response.ok) {
    throw await buildApiError(response, "Nao foi possivel gerar o contrato corrigido.");
  }

  return (await response.json()) as CorrectedContractResponse;
}

export function getDownloadCorrectedUrl(contractId: string): string {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  return `${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}/download-corrected`;
}
