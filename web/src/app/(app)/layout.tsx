import React, { type ReactNode } from "react";

import { AppShell } from "../../components/navigation/app-shell";

type LoggedAppLayoutProps = {
  children: ReactNode;
};

export default function LoggedAppLayout({ children }: LoggedAppLayoutProps) {
  return <AppShell>{children}</AppShell>;
}
