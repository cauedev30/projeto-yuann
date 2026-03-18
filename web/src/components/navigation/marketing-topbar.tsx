import React from "react";
import Link from "next/link";

export function MarketingTopbar() {
  return (
    <header className="marketingTopbar">
      <Link aria-label="LegalTech" className="marketingBrand" href="/">
        <span aria-hidden="true" className="marketingBrandMark">
          LT
        </span>
        <span className="marketingBrandText">LegalTech</span>
      </Link>
      <nav aria-label="Navegacao institucional" className="marketingNav">
        <Link href="#fluxo">Fluxo</Link>
        <Link className="primaryCta navCta" href="/dashboard">
          Workspace
        </Link>
      </nav>
    </header>
  );
}
