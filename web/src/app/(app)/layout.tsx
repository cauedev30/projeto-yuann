import React, { type ReactNode } from "react";

import { AppShell } from "../../components/navigation/app-shell";
import { AuthProvider } from "../../contexts/auth-context";
import { AuthGuard } from "../../components/guards/auth-guard";

type LoggedAppLayoutProps = {
  children: ReactNode;
};

export default function LoggedAppLayout({ children }: LoggedAppLayoutProps) {
  return (
    <AuthProvider>
      <AuthGuard>
        <AppShell>{children}</AppShell>
      </AuthGuard>
    </AuthProvider>
  );
}
