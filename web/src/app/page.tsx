import React from "react";
import Link from "next/link";

import { MarketingTopbar } from "../components/navigation/marketing-topbar";

export default function HomePage() {
  return (
    <main className="marketingPage">
      <MarketingTopbar />

      <section className="marketingHero">
        <h1>Gestao contratual simplificada.</h1>
        <p className="marketingLead">
          Entrada, triagem e acompanhamento de contratos em um unico espaço de trabalho.
        </p>
        <div className="marketingHeroActions">
          <Link className="primaryCta" href="/dashboard">
            Abrir espaço de trabalho
          </Link>
          <Link className="secondaryCta" href="#fluxo">
            Conhecer o fluxo
          </Link>
        </div>
      </section>

      <section className="marketingSection" id="fluxo">
        <h2>Da entrada ao acompanhamento</h2>
        <div className="marketingFeatures">
          <div className="marketingFeature">
            <h3>Entrada estruturada</h3>
            <p>Entrada clara para documentos com contexto minimo de revisao.</p>
          </div>
          <div className="marketingFeature">
            <h3>Triagem por risco</h3>
            <p>Pontos sensiveis identificados cedo para a decisao juridica.</p>
          </div>
          <div className="marketingFeature">
            <h3>Acompanhamento executivo</h3>
            <p>Eventos e proximos passos sob a mesma logica visual.</p>
          </div>
        </div>
      </section>

      <section className="marketingClosing">
        <h2>Organize seu portfólio contratual.</h2>
        <Link className="primaryCta" href="/contracts">
          Comece agora
        </Link>
      </section>
    </main>
  );
}
