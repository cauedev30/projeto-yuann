import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { NotificationHistory } from "./notification-history";


describe("NotificationHistory", () => {
  it("renders recipient and notification status", () => {
    render(
      <NotificationHistory
        items={[
          {
            id: "n1",
            channel: "email",
            recipient: "alerts@example.com",
            status: "success",
            sentAt: "2026-04-01T10:00:00Z",
          },
        ]}
      />,
    );

    expect(screen.getByText("alerts@example.com")).toBeInTheDocument();
    expect(screen.getByText("success")).toBeInTheDocument();
  });
});
