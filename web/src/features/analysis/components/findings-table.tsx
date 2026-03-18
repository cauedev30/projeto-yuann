import React from "react";

import type { ContractFinding } from "@/entities/contracts/model";
import styles from "./findings-table.module.css";

type FindingsTableProps = {
  items: ContractFinding[];
};

export function FindingsTable({ items }: FindingsTableProps) {
  return (
    <div className={styles.wrapper}>
      <table aria-label="Tabela de findings" className={styles.table}>
        <thead>
          <tr>
            <th scope="col">Clausula</th>
            <th scope="col">Status</th>
            <th scope="col">Risco</th>
            <th scope="col">Direcao sugerida</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={`${item.clauseName}-${item.status}`}>
              <td>{item.clauseName}</td>
              <td>{item.status}</td>
              <td>{item.riskExplanation}</td>
              <td>{item.suggestedAdjustmentDirection}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
