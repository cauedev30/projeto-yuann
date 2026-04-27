import { getClientEnv } from "../env";
import { getAuthHeaders } from "./auth";

export type AdminUser = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
};

export async function listUsers(): Promise<AdminUser[]> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const res = await fetch(`${NEXT_PUBLIC_API_URL}/api/admin/users`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Failed to load users");
  return res.json();
}

export async function createUser(payload: {
  email: string;
  password: string;
  full_name: string;
  role?: string;
}): Promise<AdminUser> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const res = await fetch(`${NEXT_PUBLIC_API_URL}/api/admin/users`, {
    method: "POST",
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create user");
  return res.json();
}

export async function updateUser(
  userId: string,
  payload: { role?: string; is_active?: boolean }
): Promise<void> {
  const { NEXT_PUBLIC_API_URL } = getClientEnv();
  const res = await fetch(`${NEXT_PUBLIC_API_URL}/api/admin/users/${userId}`, {
    method: "PATCH",
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to update user");
}
