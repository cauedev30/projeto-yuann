import React from "react";

import { EmptyState } from "../../../components/ui/empty-state";

export function EmptyDashboardState() {
  return (
    <EmptyState
      eyebrow="Sem snapshot runtime"
      title="Dashboard indisponivel no momento."
      body="Conecte uma fonte de dados em tempo real para visualizar contratos, eventos e notificacoes."
    />
  );
}
