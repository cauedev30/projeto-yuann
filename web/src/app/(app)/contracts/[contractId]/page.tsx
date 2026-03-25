import React from "react";

import { ContractDetailScreen } from "../../../../features/contracts/screens/contract-detail-screen";

type ContractDetailPageProps = {
  params: Promise<{ contractId: string }>;
  searchParams: Promise<{ versionId?: string | string[] }>;
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

  return <ContractDetailScreen contractId={contractId} versionId={versionId} />;
}
