import React from "react";
import Link from "next/link";

export function MarketingTopbar() {
  return (
    <header className="marketingTopbar">
      <Link className="marketingBrand" href="/">
        YUANN Platform
      </Link>
      <nav aria-label="Navegacao institucional" className="marketingNav">
        <Link href="#produto">Produto</Link>
        <Link href="#fluxo">Fluxo</Link>
        <Link href="/dashboard">Workspace</Link>
      </nav>
    </header>
  );
}
