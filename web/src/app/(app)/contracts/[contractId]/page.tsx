import React from "react";

import { ContractDetailScreen } from "../../../../features/contracts/screens/contract-detail-screen";

type ContractDetailPageProps = {
  params: Promise<{ contractId: string }>;
  searchParams: Promise<{ versionId?: string | string[]; context?: string | string[] }>;
};

export default async function ContractDetailPage({
  params,
  searchParams,
}: ContractDetailPageProps) {
  const { contractId } = await params;
  const resolvedSearchParams = await searchParams;
  const versionId = Array.isArray(resolvedSearchParams.versionId)
    ? resolvedSearchParams.versionId[0] ?? null
    : resolvedSearchParams.versionId ?? null;
  const context = Array.isArray(resolvedSearchParams.context)
    ? resolvedSearchParams.context[0] ?? "contracts"
    : resolvedSearchParams.context ?? "contracts";

  return <ContractDetailScreen contractId={contractId} versionId={versionId} context={context as "acervo" | "historico" | "contracts"} />;
}
