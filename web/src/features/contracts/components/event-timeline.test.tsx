import { render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { ContractEventSummary } from "../../../entities/contracts/model";
import { EventTimeline, classifyEventUrgency } from "./event-timeline";

function makeEvent(overrides: Partial<ContractEventSummary> = {}): ContractEventSummary {
  return {
    id: "evt-1",
    eventType: "renewal",
    eventDate: "2026-04-16", // 31 days from 2026-03-16
    leadTimeDays: 30,
    metadata: {},
    ...overrides,
  };
}

describe("EventTimeline", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-03-16T12:00:00Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("shows empty state when events array is empty", () => {
    render(<EventTimeline events={[]} />);
    expect(screen.getByText("Nenhum evento identificado")).toBeInTheDocument();
  });

  it("shows 'Renovação' for renewal event type", () => {
    render(<EventTimeline events={[makeEvent({ eventType: "renewal" })]} />);
    expect(screen.getByText("Renovação")).toBeInTheDocument();
  });

  it("shows 'Vencimento' for expiration event type", () => {
    render(<EventTimeline events={[makeEvent({ eventType: "expiration" })]} />);
    expect(screen.getByText("Vencimento")).toBeInTheDocument();
  });

  it("shows date formatted as DD/MM/YYYY", () => {
    render(<EventTimeline events={[makeEvent({ eventDate: "2026-06-15" })]} />);
    expect(screen.getByText("15/06/2026")).toBeInTheDocument();
  });

  it("shows 'em X dias' for future events", () => {
    // 2026-03-26 is 10 days from today (2026-03-16)
    render(<EventTimeline events={[makeEvent({ eventDate: "2026-03-26", leadTimeDays: 5 })]} />);
    expect(screen.getByText("em 10 dias")).toBeInTheDocument();
  });

  it("shows 'há X dias' for past events", () => {
    // 2026-03-06 is 10 days in the past from 2026-03-16
    render(<EventTimeline events={[makeEvent({ eventDate: "2026-03-06", leadTimeDays: 5 })]} />);
    expect(screen.getByText("há 10 dias")).toBeInTheDocument();
  });

  it("shows 'Crítico' pill for urgent events (daysUntil <= leadTimeDays)", () => {
    // 2026-03-26 is 10 days from today, leadTimeDays=30 → critical
    render(<EventTimeline events={[makeEvent({ eventDate: "2026-03-26", leadTimeDays: 30 })]} />);
    expect(screen.getByText("Crítico")).toBeInTheDocument();
  });

  it("shows 'Conforme' pill for non-urgent events", () => {
    // 2026-06-15 is 91 days from today, leadTimeDays=30 → conforme (91 > 60)
    render(<EventTimeline events={[makeEvent({ eventDate: "2026-06-15", leadTimeDays: 30 })]} />);
    expect(screen.getByText("Conforme")).toBeInTheDocument();
  });
});

describe("classifyEventUrgency", () => {
  it("returns 'critical' when daysUntil <= leadTimeDays", () => {
    expect(classifyEventUrgency(10, 30)).toBe("critical");
  });

  it("returns 'attention' when daysUntil <= leadTimeDays * 2", () => {
    expect(classifyEventUrgency(45, 30)).toBe("attention");
  });

  it("returns 'conforme' when daysUntil > leadTimeDays * 2", () => {
    expect(classifyEventUrgency(100, 30)).toBe("conforme");
  });
});
