"use client";

import React, { useCallback, useEffect, useState } from "react";

import { LoadingSkeleton } from "../../../components/ui/loading-skeleton";
import { PageHeader } from "../../../components/ui/page-header";
import { SurfaceCard } from "../../../components/ui/surface-card";
import {
  createUser,
  listUsers,
  updateUser,
  type AdminUser,
} from "../../../lib/api/admin";
import styles from "./admin-users-screen.module.css";

export function AdminUsersScreen() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "user",
  });

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listUsers();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Erro ao carregar usuários."));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await createUser(form);
      setForm({ full_name: "", email: "", password: "", role: "user" });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Erro ao criar usuário."));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleToggleActive(user: AdminUser) {
    try {
      await updateUser(user.id, { is_active: !user.is_active });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Erro ao atualizar usuário."));
    }
  }

  function handleChange(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  return (
    <div className={styles.container}>
      <PageHeader eyebrow="Admin" title="Usuários" />

      <SurfaceCard title="Novo usuário">
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formRow}>
            <label className={styles.field}>
              <span className={styles.label}>Nome completo</span>
              <input
                className={styles.input}
                type="text"
                value={form.full_name}
                onChange={(e) => handleChange("full_name", e.target.value)}
                required
              />
            </label>
            <label className={styles.field}>
              <span className={styles.label}>Email</span>
              <input
                className={styles.input}
                type="email"
                value={form.email}
                onChange={(e) => handleChange("email", e.target.value)}
                required
              />
            </label>
          </div>
          <div className={styles.formRow}>
            <label className={styles.field}>
              <span className={styles.label}>Senha</span>
              <input
                className={styles.input}
                type="password"
                value={form.password}
                onChange={(e) => handleChange("password", e.target.value)}
                required
              />
            </label>
            <label className={styles.field}>
              <span className={styles.label}>Perfil</span>
              <select
                className={styles.input}
                value={form.role}
                onChange={(e) => handleChange("role", e.target.value)}
              >
                <option value="user">Usuário</option>
                <option value="admin">Administrador</option>
              </select>
            </label>
          </div>
          <div className={styles.formActions}>
            <button
              type="submit"
              className={styles.buttonPrimary}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Criando..." : "Criar usuário"}
            </button>
          </div>
        </form>
      </SurfaceCard>

      <SurfaceCard title="Lista de usuários">
        {isLoading ? (
          <LoadingSkeleton variant="table" lines={5} />
        ) : error ? (
          <p className={styles.error}>{error.message}</p>
        ) : users.length === 0 ? (
          <p className={styles.empty}>Nenhum usuário encontrado.</p>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Email</th>
                  <th>Perfil</th>
                  <th>Ativo</th>
                  <th>Ação</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.full_name}</td>
                    <td>{user.email}</td>
                    <td>{user.role}</td>
                    <td>{user.is_active ? "Sim" : "Não"}</td>
                    <td>
                      <button
                        type="button"
                        className={
                          user.is_active
                            ? styles.buttonSecondary
                            : styles.buttonPrimary
                        }
                        onClick={() => handleToggleActive(user)}
                      >
                        {user.is_active ? "Desativar" : "Ativar"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SurfaceCard>
    </div>
  );
}
