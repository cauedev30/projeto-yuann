import React, { type ReactNode } from "react";

import "./globals.css";

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="pt-BR">
      <body className="app-root">{children}</body>
    </html>
  );
}
