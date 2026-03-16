import React from "react";
import Link from "next/link";

import { MarketingTopbar } from "../components/navigation/marketing-topbar";

export default function HomePage() {
  return (
    <main className="marketingPage">
      <MarketingTopbar />

      <section className="marketingHero">
        <div className="marketingHeroCopy">
          <p className="marketingEyebrow">Governanca executiva</p>
          <h1>Governanca contratual para times de expansao</h1>
          <p className="marketingLead">
            Estruture intake, triagem e acompanhamento de contratos em uma interface clara
            para times juridicos e operacionais.
          </p>
          <p className="marketingLead">
            Uma interface clara para revisar contratos, risco e proximas acoes.
          </p>
          <div className="marketingHeroActions">
            <Link className="primaryCta" href="/dashboard">
              Entrar no workspace
            </Link>
            <Link className="secondaryCta" href="#fluxo">
              Ver o fluxo
            </Link>
          </div>
        </div>

        <aside className="marketingHeroPanel">
          <p className="marketingPanelLabel">Workspace</p>
          <h2 className="marketingPanelTitle">
            Portifolio, triagem e proximos passos em uma so camada visual.
          </h2>
          <p className="marketingPanelBody">
            O produto combina leitura operacional, findings e monitoramento sem cair em
            um painel pesado ou em uma landing generica.
          </p>
          <div className="marketingValueList">
            <div className="marketingValueCard">
              <strong>+12 contratos</strong>
              <span>Visao executiva para areas juridicas e de expansao.</span>
            </div>
            <div className="marketingValueCard">
              <strong>3 sinais criticos</strong>
              <span>Priorizacao de risco antes da proxima rodada de analise.</span>
            </div>
          </div>
        </aside>
      </section>

      <section className="marketingSection" id="fluxo">
        <div className="marketingSectionHeader">
          <h2>Do intake ao acompanhamento</h2>
          <p>
            O produto organiza o caminho completo de decisao sem quebrar a operacao em
            telas desconectadas.
          </p>
        </div>
        <div className="marketingFeatures">
          <article className="marketingFeature">
            <h3>Upload e triagem inicial</h3>
            <p>Centralize o envio do PDF e a leitura inicial da sessao atual.</p>
          </article>
          <article className="marketingFeature">
            <h3>Politicas e findings</h3>
            <p>Organize o que exige atencao juridica sem depender de planilhas paralelas.</p>
          </article>
          <article className="marketingFeature">
            <h3>Monitoramento de eventos</h3>
            <p>Conecte contratos, riscos e proximas acoes em um unico workspace.</p>
          </article>
        </div>
      </section>

      <section className="marketingSection" id="produto">
        <div className="marketingSectionHeader">
          <h2>Workspace orientado a decisao</h2>
          <p className="marketingSectionIntro">
            A area logada herda a mesma linguagem visual da home, mas com densidade
            operacional suficiente para dashboard e contracts.
          </p>
        </div>
        <div className="marketingProof">
          <div className="marketingProofCard">
            <p className="marketingEyebrow">Direcao aprovada</p>
            <p className="marketingLead">
              Produto empresarial premium, com navegacao clara, superfícies consistentes
              e hierarquia executiva.
            </p>
          </div>
          <div className="marketingProofCard">
            <ul>
              <li>Home comercial com CTA objetivo</li>
              <li>Shell compartilhado para as areas logadas</li>
              <li>Dashboard e contracts sob a mesma identidade</li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  );
}
