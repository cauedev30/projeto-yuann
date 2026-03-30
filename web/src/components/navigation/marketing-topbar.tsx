import React from "react";
import Link from "next/link";

export function MarketingTopbar() {
  return (
    <header className="marketingTopbar">
      <Link aria-label="LegalBoard" className="marketingBrand" href="/">
        <img
          alt=""
          className="marketingBrandLogo"
          height={40}
          src="/logo.png"
          width={40}
        />
        <span className="marketingBrandText">LegalBoard</span>
      </Link>
      <nav aria-label="Navegação institucional" className="marketingNav">
        <Link href="#fluxo">Fluxo</Link>
        <Link className="primaryCta navCta" href="/dashboard">
          Espaço de trabalho
        </Link>
      </nav>
    </header>
  );
}
