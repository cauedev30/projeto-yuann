"use client";

import React from "react";
import { useId, useState } from "react";

import type { ContractSource, ContractUploadInput } from "@/entities/contracts/model";
import styles from "./upload-form.module.css";

type UploadFormProps = {
  onSubmit: (payload: ContractUploadInput) => Promise<void> | void;
  isSubmitting: boolean;
};

const contractTypeOptions: ReadonlyArray<{ value: ContractSource; label: string }> = [
  { value: "third_party_draft", label: "Minuta de terceiro" },
  { value: "signed_contract", label: "Contrato assinado" },
];

export function UploadForm({ onSubmit, isSubmitting }: UploadFormProps) {
  const titleId = useId();
  const referenceId = useId();
  const sourceId = useId();
  const fileId = useId();
  const [title, setTitle] = useState("");
  const [externalReference, setExternalReference] = useState("");
  const [source, setSource] = useState<ContractSource>("third_party_draft");
  const [file, setFile] = useState<File | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      return;
    }

    await onSubmit({
      title,
      externalReference,
      source,
      file,
    });
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.fieldsGrid}>
        <div className={styles.field}>
          <label className={styles.label} htmlFor={titleId}>
            Titulo do contrato
          </label>
          <input
            className={styles.input}
            disabled={isSubmitting}
            id={titleId}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Ex.: Loja Centro"
            value={title}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label} htmlFor={referenceId}>
            Referencia externa
          </label>
          <input
            className={styles.input}
            disabled={isSubmitting}
            id={referenceId}
            onChange={(event) => setExternalReference(event.target.value)}
            placeholder="Ex.: LOC-001"
            value={externalReference}
          />
        </div>

        <div className={`${styles.field} ${styles.fieldFull}`}>
          <label className={styles.label} htmlFor={sourceId}>
            Tipo de contrato
          </label>
          <select
            className={styles.select}
            disabled={isSubmitting}
            id={sourceId}
            value={source}
            onChange={(event) => setSource(event.target.value as ContractSource)}
          >
            {contractTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className={styles.fileBlock}>
        <div className={styles.fileHeader}>
          <label className={styles.label} htmlFor={fileId}>
            Contrato PDF
          </label>
          <span className={styles.fileBadge}>{file ? "Arquivo pronto" : "Obrigatorio"}</span>
        </div>

        <input
          accept="application/pdf"
          className={styles.fileInput}
          disabled={isSubmitting}
          id={fileId}
          type="file"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />

        <div className={styles.fileSurface}>
          <strong className={styles.fileName}>
            {file ? file.name : "Selecione um PDF para iniciar a triagem."}
          </strong>
          <p className={styles.helper}>
            Aceita apenas PDF. O arquivo enviado alimenta o resumo da sessao, os findings e o texto extraido.
          </p>
        </div>
      </div>

      <button className={styles.submitButton} disabled={isSubmitting || !file} type="submit">
        {isSubmitting ? "Processando..." : "Enviar contrato"}
      </button>
    </form>
  );
}
