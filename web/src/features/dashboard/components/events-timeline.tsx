"use client";

import React, { useState } from "react";

import type { DashboardEvent } from "@/entities/dashboard/model";
import styles from "./events-timeline.module.css";

type EventsTimelineProps = {
  events: DashboardEvent[];
  showTitle?: boolean;
};

type TimelineFilter = "all" | "overdue" | "window" | "future";

const FILTER_LABELS: Record<TimelineFilter, string> = {
  all: "Todos",
  overdue: "Vencidos",
  window: "Na janela",
  future: "Futuros",
};

function formatEventType(eventType: string): string {
  switch (eventType) {
    case "renewal":
      return "Renovacao";
    case "expiration":
      return "Expiracao";
    case "readjustment":
      return "Reajuste";
    case "grace_period_end":
      return "Fim da carencia";
    default:
      return eventType;
  }
}

function formatEventDate(eventDate: string): string {
  return new Intl.DateTimeFormat("pt-BR").format(new Date(`${eventDate}T00:00:00`));
}

function buildOperationalLabel(event: DashboardEvent): string {
  if (event.isOverdue) {
    return `Atrasado ha ${Math.abs(event.daysUntilDue)} dias`;
  }
  if (event.daysUntilDue <= event.leadTimeDays) {
    return `Dentro da janela de alerta (${event.daysUntilDue} dias)`;
  }
  return `Previsto para ${event.daysUntilDue} dias`;
}

function matchesFilter(event: DashboardEvent, filter: TimelineFilter): boolean {
  if (filter === "all") {
    return true;
  }
  if (filter === "overdue") {
    return event.isOverdue;
  }
  if (filter === "window") {
    return !event.isOverdue && event.daysUntilDue <= event.leadTimeDays;
  }
  return !event.isOverdue && event.daysUntilDue > event.leadTimeDays;
}

export function EventsTimeline({ events, showTitle = true }: EventsTimelineProps) {
  const [activeFilter, setActiveFilter] = useState<TimelineFilter>("all");
  const orderedEvents = [...events].sort((left, right) => left.eventDate.localeCompare(right.eventDate));
  const visibleEvents = orderedEvents.filter((event) => matchesFilter(event, activeFilter));

  return (
    <section className={styles.section}>
      {showTitle ? <h2>Timeline de eventos</h2> : null}

      <div className={styles.filters} role="toolbar" aria-label="Filtros da timeline">
        {(Object.keys(FILTER_LABELS) as TimelineFilter[]).map((filter) => (
          <button
            key={filter}
            className={activeFilter === filter ? styles.filterButtonActive : styles.filterButton}
            onClick={() => setActiveFilter(filter)}
            type="button"
          >
            {FILTER_LABELS[filter]}
          </button>
        ))}
      </div>

      {visibleEvents.length === 0 ? (
        <p className={styles.emptyState}>Nenhum evento operacional encontrado para o filtro atual.</p>
      ) : (
        <ul className={styles.list}>
          {visibleEvents.map((event) => (
            <li key={event.id} className={styles.item}>
              <div className={styles.itemTop}>
                <strong>{formatEventType(event.eventType)}</strong>
                <span>{formatEventDate(event.eventDate)}</span>
              </div>
              <p className={styles.contractText}>
                {event.contractTitle} <span>{event.externalReference}</span>
              </p>
              <p className={styles.metaText}>{buildOperationalLabel(event)}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
