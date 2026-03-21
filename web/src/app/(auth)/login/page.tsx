"use client";

import React, { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "../../../contexts/auth-context";
import styles from "./page.module.css";

export default function LoginPage() {
  const { login, register } = useAuth();
  const router = useRouter();

  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (isRegisterMode) {
        await register(email, password, fullName);
      } else {
        await login(email, password);
      }
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro inesperado.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.brand}>
          <img
            alt=""
            className={styles.brandLogo}
            height={60}
            src="/logo.png"
            width={60}
          />
          <span className={styles.brandText}>LegalBoard</span>
        </div>

        <h1 className={styles.title}>
          {isRegisterMode ? "Criar conta" : "Entrar"}
        </h1>
        <p className={styles.subtitle}>
          {isRegisterMode
            ? "Preencha os dados para criar sua conta"
            : "Acesse sua plataforma de gestao contratual"}
        </p>

        {error && <div className={styles.error}>{error}</div>}

        <form className={styles.form} onSubmit={handleSubmit}>
          {isRegisterMode && (
            <div className={styles.field}>
              <label className={styles.label} htmlFor="fullName">
                Nome completo
              </label>
              <input
                className={styles.input}
                id="fullName"
                type="text"
                placeholder="Seu nome"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>
          )}

          <div className={styles.field}>
            <label className={styles.label} htmlFor="email">
              Email
            </label>
            <input
              className={styles.input}
              id="email"
              type="email"
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="password">
              Senha
            </label>
            <input
              className={styles.input}
              id="password"
              type="password"
              placeholder="Sua senha"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          <button
            className={styles.submitButton}
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Aguarde..."
              : isRegisterMode
                ? "Criar conta"
                : "Entrar"}
          </button>
        </form>

        <div className={styles.toggleMode}>
          {isRegisterMode ? "Ja tem conta? " : "Nao tem conta? "}
          <button
            className={styles.toggleButton}
            type="button"
            onClick={() => {
              setIsRegisterMode(!isRegisterMode);
              setError(null);
            }}
          >
            {isRegisterMode ? "Entrar" : "Criar conta"}
          </button>
        </div>
      </div>
    </div>
  );
}
