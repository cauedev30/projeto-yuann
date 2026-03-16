import React from "react";

import { PageHeader } from "../../../../components/ui/page-header";
import { SurfaceCard } from "../../../../components/ui/surface-card";

type ContractDetailPageProps = {
  params: Promise<{ contractId: string }>;
};

export default async function ContractDetailPage({ params }: ContractDetailPageProps) {
  const { contractId } = await params;

  return (
    <section>
      <PageHeader
        eyebrow="Contracts"
        title={contractId}
        description="Detalhe do contrato ainda em placeholder, mas agora dentro da moldura compartilhada do workspace."
      />

      <SurfaceCard>
        <p>A timeline detalhada e os findings persistidos entram na proxima iteracao.</p>
      </SurfaceCard>
    </section>
  );
}
