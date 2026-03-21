import React, { type ReactNode } from "react";
import { DM_Sans } from "next/font/google";

import "./globals.css";
import { QueryProvider } from "@/lib/query-provider";

const dmSans = DM_Sans({ subsets: ["latin"], weight: ["400", "500", "700"] });

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="pt-BR" className={dmSans.className}>
      <body className="app-root">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
