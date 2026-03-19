"use client";

import React, { type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../contexts/auth-context";

type AuthGuardProps = {
  children: ReactNode;
};

export function AuthGuard({ children }: AuthGuardProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  React.useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  if (!mounted) {
    return null;
  }

  if (isLoading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", color: "var(--ink-soft)" }}>
        Carregando...
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
