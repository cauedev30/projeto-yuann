import React from "react";
import Link from "next/link";

export function MarketingTopbar() {
  return (
    <header className="marketingTopbar">
      <Link aria-label="LegalBoard" className="marketingBrand" href="/">
        <span aria-hidden="true" className="marketingBrandMark">
          LB
        </span>
        <span className="marketingBrandText">LegalBoard</span>
      </Link>
      <nav aria-label="Navegacao institucional" className="marketingNav">
        <Link href="#fluxo">Fluxo</Link>
        <Link className="primaryCta navCta" href="/dashboard">
          Espaço de trabalho
        </Link>
      </nav>
    </header>
  );
}
