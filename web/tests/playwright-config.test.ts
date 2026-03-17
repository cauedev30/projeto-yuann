import { describe, expect, it } from "vitest";

import config from "../playwright.config";

describe("playwright release configuration", () => {
  it("runs the end-to-end suite in a single worker", () => {
    expect(config.workers).toBe(1);
  });
});
