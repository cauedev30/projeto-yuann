import React from "react";

import { EmptyState } from "../../../components/ui/empty-state";
import { SurfaceCard } from "../../../components/ui/surface-card";
import type { ContractEventSummary, ContractEventType } from "../../../entities/contracts/model";
import styles from "./event-timeline.module.css";

type EventTimelineProps = {
  events?: ContractEventSummary[];
};

export type Urgency = "critical" | "attention" | "conforme";

export function classifyEventUrgency(daysUntil: number, leadTimeDays: number): Urgency {
  if (daysUntil <= leadTimeDays) return "critical";
  if (daysUntil <= leadTimeDays * 2) return "attention";
  return "conforme";
}

const EVENT_LABELS: Record<ContractEventType, string> = {
  renewal: "Renovação",
  expiration: "Vencimento",
  readjustment: "Reajuste",
  grace_period_end: "Fim da carência",
};

const URGENCY_LABELS: Record<Urgency, string> = {
  critical: "Crítico",
  attention: "Atenção",
  conforme: "Conforme",
};

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "Data não definida";
  const [year, month, day] = dateStr.split("-");
  return `${day}/${month}/${year}`;
}

function computeDaysUntil(eventDate: string | null): number | null {
  if (!eventDate) return null;
  const today = new Date("2026-03-16");
  const target = new Date(eventDate);
  const diffMs = target.getTime() - today.getTime();
  return Math.round(diffMs / (1000 * 60 * 60 * 24));
}

function formatDaysRemaining(daysUntil: number | null): string {
  if (daysUntil === null) return "Data não definida";
  if (daysUntil === 0) return "hoje";
  if (daysUntil > 0) return `em ${daysUntil} dias`;
  return `há ${Math.abs(daysUntil)} dias`;
}

type EventNodeProps = {
  event: ContractEventSummary;
};

function EventNode({ event }: EventNodeProps) {
  const daysUntil = computeDaysUntil(event.eventDate);
  const urgency =
    daysUntil !== null
      ? classifyEventUrgency(daysUntil, event.leadTimeDays)
      : "conforme";

  return (
    <li className={styles.node}>
      <span className={`${styles.circle} ${styles[urgency]}`} aria-hidden="true" />
      <div className={styles.nodeContent}>
        <div className={styles.nodeHeader}>
          <span className={styles.nodeTitle}>{EVENT_LABELS[event.eventType]}</span>
          <span className={`${styles.pill} ${styles[`pill_${urgency}`]}`}>
            {URGENCY_LABELS[urgency]}
          </span>
        </div>
        <span className={styles.nodeDate}>{formatDate(event.eventDate)}</span>
        <span className={styles.nodeDays}>{formatDaysRemaining(daysUntil)}</span>
      </div>
    </li>
  );
}

export function EventTimeline({ events = [] }: EventTimelineProps) {
  return (
    <SurfaceCard title="Eventos críticos">
      {events.length === 0 ? (
        <EmptyState
          title="Nenhum evento identificado"
          body="Nenhum evento identificado para este contrato."
        />
      ) : (
        <ol className={styles.timeline}>
          {events.map((event) => (
            <EventNode key={event.id} event={event} />
          ))}
        </ol>
      )}
    </SurfaceCard>
  );
}
