"use client";

import React, { type ReactNode } from "react";

import { AuthProvider } from "../../contexts/auth-context";

type AuthLayoutProps = {
  children: ReactNode;
};

export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}
