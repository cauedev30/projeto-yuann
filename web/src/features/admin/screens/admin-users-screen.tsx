"use client";

import React, { useCallback, useEffect, useState } from "react";
import { PageHeader } from "../../../components/ui/page-header";
import { SurfaceCard } from "../../../components/ui/surface-card";
import { LoadingSkeleton } from "../../../components/ui/loading-skeleton";
import { createUser, listUsers, updateUser, type AdminUser } from "../../../lib/api/admin";
import styles from "./admin-users-screen.module.css";

export function AdminUsersScreen() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ email: "", password: "", full_name: "", role: "user" });

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await listUsers();
      setUsers(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createUser(form);
      setForm({ email: "", password: "", full_name: "", role: "user" });
      await load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erro");
    }
  }

  async function toggleActive(user: AdminUser) {
    try {
      await updateUser(user.id, { is_active: !user.is_active });
      await load();
    } catch (e) {
      alert(e instanceof Error ? e.message : "Erro");
    }
  }

  return (
    <section className={styles.page}>
      <PageHeader eyebrow="Admin" title="Usuários" description="Gerenciar contas de acesso." />

      <SurfaceCard title="Criar usuário">
        <form onSubmit={handleCreate} className={styles.form}>
          <input placeholder="Nome completo" value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} required />
          <input placeholder="Email" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required />
          <input placeholder="Senha" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required />
          <select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
            <option value="user">Usuário</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit">Criar</button>
        </form>
      </SurfaceCard>

      <SurfaceCard title="Lista de usuários">
        {isLoading ? <LoadingSkeleton heading lines={3} /> : error ? (
          <p className={styles.alert}>{error}</p>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr><th>Nome</th><th>Email</th><th>Role</th><th>Ativo</th><th>Ações</th></tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td>{u.full_name}</td>
                  <td>{u.email}</td>
                  <td>{u.role}</td>
                  <td>{u.is_active ? "Sim" : "Não"}</td>
                  <td>
                    <button onClick={() => toggleActive(u)}>
                      {u.is_active ? "Desativar" : "Ativar"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </SurfaceCard>
    </section>
  );
}
