import React from "react";
import Link from "next/link";

import { MarketingTopbar } from "../components/navigation/marketing-topbar";

export default function HomePage() {
  return (
    <main>
      <MarketingTopbar />

      <section>
        <p>Governanca executiva</p>
        <h1>Governanca contratual para times de expansao</h1>
        <p>
          Estruture intake, triagem e acompanhamento de contratos em uma interface clara
          para times juridicos e operacionais.
        </p>
        <Link href="/dashboard">Entrar no workspace</Link>
      </section>

      <section id="fluxo">
        <h2>Do intake ao acompanhamento</h2>
        <div>
          <article>
            <h3>Upload e triagem inicial</h3>
            <p>Centralize o envio do PDF e a leitura inicial da sessao atual.</p>
          </article>
          <article>
            <h3>Politicas e findings</h3>
            <p>Organize o que exige atencao juridica sem depender de planilhas paralelas.</p>
          </article>
          <article>
            <h3>Monitoramento de eventos</h3>
            <p>Conecte contratos, riscos e proximas acoes em um unico workspace.</p>
          </article>
        </div>
      </section>

      <section id="produto">
        <h2>Workspace orientado a decisao</h2>
        <p>Leve a operacao de contratos para um fluxo unico, mais confiavel e rastreavel.</p>
      </section>
    </main>
  );
}
