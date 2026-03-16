import { getClientEnv } from "../env";
import {
  type ContractUploadInput,
  type ContractUploadResponsePayload,
  type ContractUploadResult,
  mapUploadResponseToContractUploadResult,
} from "../../entities/contracts/model";

const GENERIC_UPLOAD_ERROR = "Nao foi possivel enviar o contrato.";

function mapUploadErrorDetail(detail: unknown): string | null {
  if (detail === "Uploaded file is not a readable PDF") {
    return "O arquivo enviado nao e um PDF legivel.";
  }

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  return null;
}

async function getUploadErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    return mapUploadErrorDetail(payload.detail) ?? GENERIC_UPLOAD_ERROR;
  } catch {
    return GENERIC_UPLOAD_ERROR;
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
    throw new Error(await getUploadErrorMessage(response));
  }

  const payload = (await response.json()) as ContractUploadResponsePayload;
  return mapUploadResponseToContractUploadResult(payload);
}
