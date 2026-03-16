import React from "react";
import Link from "next/link";

import { MarketingTopbar } from "../components/navigation/marketing-topbar";

export default function HomePage() {
  return (
    <main className="marketingPage">
      <MarketingTopbar />

      <section className="marketingHero">
        <div className="marketingHeroCopy">
          <p className="marketingEyebrow">Plataforma juridica operacional</p>
          <h1>A materia contratual em formato de decisao.</h1>
          <p className="marketingLead">
            Leitura juridica, trilha operacional e proximas acoes em uma mesma
            cadencia visual.
          </p>
          <p className="marketingSublead">
            LegalTech organiza intake, risco, aprovacao e acompanhamento em um
            workspace escuro, sofisticado e construido para times que precisam decidir
            sem perder contexto.
          </p>
          <div className="marketingHeroActions">
            <Link className="primaryCta" href="/dashboard">
              Abrir workspace
            </Link>
            <Link className="secondaryCta" href="#fluxo">
              Explorar o fluxo
            </Link>
          </div>
          <div className="marketingHeroNotes">
            <span>Intake estruturado</span>
            <span>Triagem orientada por politica</span>
            <span>Ritmo executivo de acompanhamento</span>
          </div>
        </div>

        <aside className="marketingHeroPanel">
          <div className="marketingPanelFrame">
            <p className="marketingPanelLabel">Mesa viva</p>
            <h2 className="marketingPanelTitle">
              Termos, risco e proximos marcos sob a mesma pauta.
            </h2>
            <p className="marketingPanelBody">
              O visual nao imita um dashboard comum: ele conduz leitura, contexto e
              prioridade com mais cadencia editorial e menos ruido.
            </p>
          </div>

          <div className="marketingValueList">
            <div className="marketingValueCard">
              <strong>12</strong>
              <span>Dossies em revisao no workspace.</span>
            </div>
            <div className="marketingValueCard">
              <strong>03</strong>
              <span>Pontos de risco exigindo rodada juridica.</span>
            </div>
            <div className="marketingValueCard">
              <strong>48h</strong>
              <span>Janela operacional para a proxima decisao.</span>
            </div>
          </div>

          <div className="marketingLedger">
            <div className="marketingLedgerRow">
              <span>Triagem inicial</span>
              <strong>Em pauta</strong>
            </div>
            <div className="marketingLedgerRow">
              <span>Renovacao critica</span>
              <strong>2 sinais</strong>
            </div>
            <div className="marketingLedgerRow">
              <span>Historico acionavel</span>
              <strong>Consolidado</strong>
            </div>
          </div>
        </aside>
      </section>

      <section className="marketingSection" id="fluxo">
        <div className="marketingSectionHeader">
          <div>
            <p className="marketingSectionKicker">Fluxo continuo</p>
            <h2>Do intake ao acompanhamento</h2>
          </div>
          <p>
            Uma estrutura unica para intake, leitura juridica e acompanhamento sem
            espalhar o trabalho em telas desconectadas.
          </p>
        </div>
        <div className="marketingFeatures">
          <article className="marketingFeature">
            <h3>Intake com lastro operacional</h3>
            <p>Entrada clara para PDF, origem do documento e contexto minimo de revisao.</p>
          </article>
          <article className="marketingFeature">
            <h3>Triagem orientada por risco</h3>
            <p>Encontrar pontos sensiveis cedo o suficiente para sustentar a decisao juridica.</p>
          </article>
          <article className="marketingFeature">
            <h3>Acompanhamento com trilha executiva</h3>
            <p>Eventos, notificacoes e proximos passos sob a mesma logica visual.</p>
          </article>
        </div>
      </section>

      <section className="marketingEditorialBand" id="produto">
        <div className="marketingEditorialQuote">
          <p className="marketingPanelLabel">Direcao aprovada</p>
          <h2>Um produto juridico premium, nao uma landing intercambiavel.</h2>
          <p>
            A mesma identidade percorre a home, o dashboard e a mesa de contracts:
            tipografia com presenca, superficies escuras, textura discreta e hierarquia
            precisa.
          </p>
        </div>
        <div className="marketingProof">
          <div className="marketingProofCard">
            <p className="marketingProofLabel">Ritmo visual</p>
            <strong>Editorial, controlado e juridico.</strong>
            <span>Composicao assimetrica, mas ainda objetiva para leitura de produto.</span>
          </div>
          <div className="marketingProofCard">
            <p className="marketingProofLabel">Camada operacional</p>
            <strong>Dashboard e contracts no mesmo enquadramento.</strong>
            <span>Uma linguagem unica para risco, revisao e proxima acao.</span>
          </div>
          <div className="marketingProofCard">
            <p className="marketingProofLabel">Acabamento</p>
            <strong>Tipografia forte e interacao discreta.</strong>
            <span>Sem efeitos vazios e sem cara de template de IA.</span>
          </div>
        </div>
      </section>

      <section className="marketingClosing">
        <div>
          <p className="marketingSectionKicker">LegalTech workspace</p>
          <h2>Entre no produto e valide o fluxo na pratica.</h2>
        </div>
        <Link className="primaryCta" href="/dashboard">
          Ir para o dashboard
        </Link>
      </section>
    </main>
  );
}
