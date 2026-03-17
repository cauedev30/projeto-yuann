import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { EventsTimeline } from "./events-timeline";


describe("EventsTimeline", () => {
  it("shows renewal and expiration events in chronological order", () => {
    render(
      <EventsTimeline
        events={[
          {
            id: "2",
            eventType: "expiration",
            eventDate: "2031-03-31",
            leadTimeDays: 30,
            contractId: "ctr-2",
            contractTitle: "Loja Norte",
            externalReference: "LOC-002",
            daysUntilDue: 180,
            isOverdue: false,
          },
          {
            id: "1",
            eventType: "renewal",
            eventDate: "2030-09-30",
            leadTimeDays: 45,
            contractId: "ctr-1",
            contractTitle: "Loja Centro",
            externalReference: "LOC-001",
            daysUntilDue: -5,
            isOverdue: true,
          },
        ]}
      />,
    );

    const items = screen.getAllByRole("listitem");
    expect(items[0]).toHaveTextContent("Renovacao");
    expect(items[1]).toHaveTextContent("Expiracao");
    expect(items[0]).toHaveTextContent("Loja Centro");
  });

  it("filters events by operational status", async () => {
    const user = userEvent.setup();

    render(
      <EventsTimeline
        events={[
          {
            id: "1",
            eventType: "renewal",
            eventDate: "2030-09-30",
            leadTimeDays: 45,
            contractId: "ctr-1",
            contractTitle: "Loja Centro",
            externalReference: "LOC-001",
            daysUntilDue: -5,
            isOverdue: true,
          },
          {
            id: "2",
            eventType: "expiration",
            eventDate: "2030-10-10",
            leadTimeDays: 30,
            contractId: "ctr-2",
            contractTitle: "Loja Norte",
            externalReference: "LOC-002",
            daysUntilDue: 10,
            isOverdue: false,
          },
          {
            id: "3",
            eventType: "readjustment",
            eventDate: "2030-12-10",
            leadTimeDays: 15,
            contractId: "ctr-3",
            contractTitle: "Loja Sul",
            externalReference: "LOC-003",
            daysUntilDue: 90,
            isOverdue: false,
          },
        ]}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Vencidos" }));

    expect(screen.getByText("Loja Centro")).toBeInTheDocument();
    expect(screen.queryByText("Loja Norte")).not.toBeInTheDocument();
    expect(screen.queryByText("Loja Sul")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Futuros" }));

    expect(screen.getByText("Loja Sul")).toBeInTheDocument();
    expect(screen.queryByText("Loja Centro")).not.toBeInTheDocument();
  });
});
