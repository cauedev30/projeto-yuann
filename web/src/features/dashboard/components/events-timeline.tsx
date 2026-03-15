import React from "react";

import type { DashboardEvent } from "@/lib/api/dashboard";

type EventsTimelineProps = {
  events: DashboardEvent[];
};

export function EventsTimeline({ events }: EventsTimelineProps) {
  const orderedEvents = [...events].sort((left, right) => left.eventDate.localeCompare(right.eventDate));

  return (
    <section>
      <h2>Timeline de eventos</h2>
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
