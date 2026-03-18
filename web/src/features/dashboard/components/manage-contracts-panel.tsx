"use client";

import React, { useEffect, useState } from "react";
import {
  deleteContract,
  listContracts,
  updateContract,
} from "../../../lib/api/contracts";
import type { ContractListItemSummary } from "../../../entities/contracts/model";
import styles from "./manage-contracts-panel.module.css";
import { SurfaceCard } from "../../../components/ui/surface-card";

type ManageContractsPanelProps = {
  onClose: () => void;
  onRefresh: () => void;
};

export function ManageContractsPanel({ onClose, onRefresh }: ManageContractsPanelProps) {
  const [contracts, setContracts] = useState<ContractListItemSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);

  // Edit form state
  const [editTitle, setEditTitle] = useState("");
  const [editSignature, setEditSignature] = useState("");
  const [editStart, setEditStart] = useState("");
  const [editEnd, setEditEnd] = useState("");
  const [editMonths, setEditMonths] = useState<number | "">("");

  useEffect(() => {
    let isActive = true;
    async function load() {
      try {
        const response = await listContracts();
        if (isActive) setContracts(response.items);
      } catch (err) {
        console.error("Failed to load contracts", err);
      } finally {
        if (isActive) setIsLoading(false);
      }
    }
    void load();
    return () => {
      isActive = false;
    };
  }, []);

  async function handleDelete(id: string) {
    if (!window.confirm("Tem certeza que deseja apagar este contrato? Os dados nao poderao ser recuperados.")) return;
    try {
      await deleteContract(id);
      setContracts((prev) => prev.filter((c) => c.id !== id));
      onRefresh();
    } catch (err) {
      alert("Erro ao excluir contrato.");
    }
  }

  function startEdit(contract: ContractListItemSummary) {
    setEditingId(contract.id);
    setEditTitle(contract.title || "");
    setEditSignature(contract.signatureDate || "");
    setEditStart(contract.startDate || "");
    setEditEnd(contract.endDate || "");
    setEditMonths(contract.termMonths ?? "");
  }

  function cancelEdit() {
    setEditingId(null);
  }

  async function handleSaveEdit(id: string) {
    try {
      await updateContract(id, {
        title: editTitle || undefined,
        signatureDate: editSignature || null,
        startDate: editStart || null,
        endDate: editEnd || null,
        termMonths: editMonths === "" ? null : Number(editMonths),
      });
      setEditingId(null);
      // Reload contracts here
      const response = await listContracts();
      setContracts(response.items);
      onRefresh();
    } catch (err) {
      alert("Erro ao atualizar contrato.");
    }
  }

  return (
    <SurfaceCard title="Gerenciar Portfolio">
      <div className={styles.headerRow}>
        <p className={styles.description}>
          Edite as informacoes contratuais ou apague registros da sua base de dados.
        </p>
        <button className={styles.closeButton} onClick={onClose}>
          Fechar gerenciador
        </button>
      </div>

      {isLoading ? (
        <p className={styles.loadingCopy}>Carregando base de contratos...</p>
      ) : contracts.length === 0 ? (
        <p className={styles.emptyCopy}>Nenhum contrato persistido no momento.</p>
      ) : (
        <div className={styles.list}>
          {contracts.map((contract) => (
            <div key={contract.id} className={styles.row}>
              {editingId === contract.id ? (
                <div className={styles.editForm}>
                  <div className={styles.fieldGroup}>
                    <label>Titulo do Contrato</label>
                    <input
                      className={styles.input}
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                    />
                  </div>
                  <div className={styles.dateGrid}>
                    <div className={styles.fieldGroup}>
                      <label>Data Assinatura</label>
                      <input
                        type="date"
                        className={styles.input}
                        value={editSignature}
                        onChange={(e) => setEditSignature(e.target.value)}
                      />
                    </div>
                    <div className={styles.fieldGroup}>
                      <label>Inicio Vigencia</label>
                      <input
                        type="date"
                        className={styles.input}
                        value={editStart}
                        onChange={(e) => setEditStart(e.target.value)}
                      />
                    </div>
                    <div className={styles.fieldGroup}>
                      <label>Fim Vigencia</label>
                      <input
                        type="date"
                        className={styles.input}
                        value={editEnd}
                        onChange={(e) => setEditEnd(e.target.value)}
                      />
                    </div>
                    <div className={styles.fieldGroup}>
                      <label>Prazo (Meses)</label>
                      <input
                        type="number"
                        className={styles.input}
                        value={editMonths}
                        onChange={(e) => setEditMonths(e.target.value ? Number(e.target.value) : "")}
                      />
                    </div>
                  </div>
                  <div className={styles.actionRow}>
                    <button className={styles.btnSave} onClick={() => void handleSaveEdit(contract.id)}>
                      Salvar alteracoes
                    </button>
                    <button className={styles.btnCancel} onClick={cancelEdit}>
                      Cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <div className={styles.viewState}>
                  <div>
                    <strong className={styles.contractTitle}>{contract.title}</strong>
                    <div className={styles.metaInfo}>
                      <span>Ref: {contract.externalReference}</span>
                      {contract.signatureDate && <span> • Assinatura: {contract.signatureDate}</span>}
                    </div>
                  </div>
                  <div className={styles.actionRow}>
                    <button className={styles.btnEdit} onClick={() => startEdit(contract)}>
                      Editar
                    </button>
                    <button className={styles.btnDelete} onClick={() => void handleDelete(contract.id)}>
                      Deletar
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </SurfaceCard>
  );
}
