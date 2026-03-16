import React from "react";

import type { DashboardEvent } from "@/entities/dashboard/model";

type EventsTimelineProps = {
  events: DashboardEvent[];
  showTitle?: boolean;
};

export function EventsTimeline({ events, showTitle = true }: EventsTimelineProps) {
  const orderedEvents = [...events].sort((left, right) => left.eventDate.localeCompare(right.eventDate));

  return (
    <section>
      {showTitle ? <h2>Timeline de eventos</h2> : null}
      <ul>
        {orderedEvents.map((event) => (
          <li key={event.id}>
            <strong>{event.eventType}</strong> <span>{event.eventDate}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
