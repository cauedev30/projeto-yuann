"use client";

import React from "react";
import { useId, useState } from "react";

import type { ContractSource, ContractUploadInput } from "@/lib/api/contracts";

type UploadFormProps = {
  onSubmit: (payload: ContractUploadInput) => Promise<void> | void;
  isSubmitting: boolean;
};

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
    <form onSubmit={handleSubmit}>
      <label htmlFor={titleId}>Titulo do contrato</label>
      <input id={titleId} value={title} onChange={(event) => setTitle(event.target.value)} />

      <label htmlFor={referenceId}>Referencia externa</label>
      <input
        id={referenceId}
        value={externalReference}
        onChange={(event) => setExternalReference(event.target.value)}
      />

      <label htmlFor={sourceId}>Tipo de contrato</label>
      <select
        id={sourceId}
        value={source}
        onChange={(event) => setSource(event.target.value as ContractSource)}
      >
        <option value="third_party_draft">third_party_draft</option>
        <option value="signed_contract">signed_contract</option>
      </select>

      <label htmlFor={fileId}>Contrato PDF</label>
      <input
        id={fileId}
        type="file"
        accept="application/pdf"
        onChange={(event) => setFile(event.target.files?.[0] ?? null)}
      />

      <button disabled={isSubmitting || !file} type="submit">
        {isSubmitting ? "Enviando..." : "Enviar contrato"}
      </button>
    </form>
  );
}
