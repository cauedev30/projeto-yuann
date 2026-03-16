import { getClientEnv } from "../env";
import {
  type ContractDetail,
  type ContractDetailResponsePayload,
  type ContractListResponse,
  type ContractListResponsePayload,
  type ContractUploadInput,
  type ContractUploadResponsePayload,
  type ContractUploadResult,
  mapContractDetailResponse,
  mapContractListResponse,
  mapUploadResponseToContractUploadResult,
} from "../../entities/contracts/model";

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
    body: formData,
  });

  if (!response.ok) {
    throw await buildApiError(response, GENERIC_UPLOAD_ERROR, mapUploadErrorDetail);
  }

  const payload = (await response.json()) as ContractUploadResponsePayload;
  return mapUploadResponseToContractUploadResult(payload);
}

export async function listContracts(
  fetchImpl: typeof fetch = fetch,
): Promise<ContractListResponse> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/contracts`);

  if (!response.ok) {
    throw await buildApiError(response, GENERIC_LIST_ERROR);
  }

  const payload = (await response.json()) as ContractListResponsePayload;
  return mapContractListResponse(payload);
}

export async function getContractDetail(
  contractId: string,
  fetchImpl: typeof fetch = fetch,
): Promise<ContractDetail> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetchImpl(`${NEXT_PUBLIC_API_URL}/api/contracts/${contractId}`);

  if (!response.ok) {
    throw await buildApiError(response, GENERIC_DETAIL_ERROR);
  }

  const payload = (await response.json()) as ContractDetailResponsePayload;
  return mapContractDetailResponse(payload);
}
