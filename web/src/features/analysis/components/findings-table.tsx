import React from "react";

import type { FindingItem } from "@/lib/api/contracts";

type FindingsTableProps = {
  items: FindingItem[];
};

export function FindingsTable({ items }: FindingsTableProps) {
  return (
    <table>
      <thead>
        <tr>
          <th>Clausula</th>
          <th>Status</th>
          <th>Risco</th>
          <th>Direcao sugerida</th>
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
  );
}
