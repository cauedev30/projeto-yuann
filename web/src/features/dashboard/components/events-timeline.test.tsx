import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EventsTimeline } from "./events-timeline";


describe("EventsTimeline", () => {
  it("shows renewal and expiration events in chronological order", () => {
    render(
      <EventsTimeline
        events={[
          { id: "2", eventType: "expiration", eventDate: "2031-03-31" },
          { id: "1", eventType: "renewal", eventDate: "2030-09-30" },
        ]}
      />,
    );

    const items = screen.getAllByRole("listitem");
    expect(items[0]).toHaveTextContent("renewal");
    expect(items[1]).toHaveTextContent("expiration");
  });
});
