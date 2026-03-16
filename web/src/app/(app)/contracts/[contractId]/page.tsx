import React from "react";

import { ContractDetailScreen } from "../../../../features/contracts/screens/contract-detail-screen";

type ContractDetailPageProps = {
  params: Promise<{ contractId: string }>;
};

export default async function ContractDetailPage({ params }: ContractDetailPageProps) {
  const { contractId } = await params;

  return <ContractDetailScreen contractId={contractId} />;
}
