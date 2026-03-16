import { getClientEnv } from "../env";
import {
  type ContractUploadInput,
  type ContractUploadResponsePayload,
  type ContractUploadResult,
  mapUploadResponseToContractUploadResult,
} from "../../entities/contracts/model";

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
    throw new Error("Nao foi possivel enviar o contrato.");
  }

  const payload = (await response.json()) as ContractUploadResponsePayload;
  return mapUploadResponseToContractUploadResult(payload);
}
