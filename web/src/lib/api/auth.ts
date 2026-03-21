import { getClientEnv } from "../env";

export type AuthResponse = {
  accessToken: string;
  tokenType: string;
  userId: string;
  email: string;
  fullName: string;
};

type AuthResponsePayload = {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  full_name: string;
};

export type AuthUser = {
  id: string;
  email: string;
  fullName: string;
  isActive: boolean;
};

type UserPayload = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
};

function mapAuthResponse(payload: AuthResponsePayload): AuthResponse {
  return {
    accessToken: payload.access_token,
    tokenType: payload.token_type,
    userId: payload.user_id,
    email: payload.email,
    fullName: payload.full_name,
  };
}

function mapUser(payload: UserPayload): AuthUser {
  return {
    id: payload.id,
    email: payload.email,
    fullName: payload.full_name,
    isActive: payload.is_active,
  };
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("legalboard_token");
}

export function getAuthHeaders(): Record<string, string> {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function loginApi(
  email: string,
  password: string,
): Promise<AuthResponse> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetch(`${NEXT_PUBLIC_API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(
      (payload as { detail?: string }).detail || "Falha ao fazer login.",
    );
  }

  const payload = (await response.json()) as AuthResponsePayload;
  return mapAuthResponse(payload);
}

export async function registerApi(
  email: string,
  password: string,
  fullName: string,
): Promise<AuthResponse> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const response = await fetch(`${NEXT_PUBLIC_API_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(
      (payload as { detail?: string }).detail || "Falha ao registrar.",
    );
  }

  const payload = (await response.json()) as AuthResponsePayload;
  return mapAuthResponse(payload);
}

export async function getMeApi(): Promise<AuthUser> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const token = getStoredToken();
  const response = await fetch(`${NEXT_PUBLIC_API_URL}/api/auth/me`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (!response.ok) {
    throw new Error("Not authenticated");
  }

  const payload = (await response.json()) as UserPayload;
  return mapUser(payload);
}
