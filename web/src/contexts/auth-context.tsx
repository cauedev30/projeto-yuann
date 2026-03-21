"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  type AuthResponse,
  type AuthUser,
  getMeApi,
  loginApi,
  registerApi,
} from "../lib/api/auth";

type AuthState = {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(() => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("legalboard_token");
  });
  const [isLoading, setIsLoading] = useState(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem("legalboard_token") !== null;
  });

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    getMeApi()
      .then((u) => { if (!cancelled) setUser(u); })
      .catch(() => {
        if (cancelled) return;
        localStorage.removeItem("legalboard_token");
        setToken(null);
      })
      .finally(() => { if (!cancelled) setIsLoading(false); });
    return () => { cancelled = true; };
  }, [token]);

  const handleAuthSuccess = useCallback((res: AuthResponse) => {
    localStorage.setItem("legalboard_token", res.accessToken);
    setToken(res.accessToken);
    setUser({
      id: res.userId,
      email: res.email,
      fullName: res.fullName,
      isActive: true,
    });
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await loginApi(email, password);
      handleAuthSuccess(res);
    },
    [handleAuthSuccess],
  );

  const register = useCallback(
    async (email: string, password: string, fullName: string) => {
      const res = await registerApi(email, password, fullName);
      handleAuthSuccess(res);
    },
    [handleAuthSuccess],
  );

  const logout = useCallback(() => {
    localStorage.removeItem("legalboard_token");
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, token, isLoading, login, register, logout }),
    [user, token, isLoading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
