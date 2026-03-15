import { describe, expect, it } from "vitest";

import { loadClientEnv } from "../src/lib/env";

describe("loadClientEnv", () => {
  it("requires NEXT_PUBLIC_API_URL", () => {
    expect(() => loadClientEnv({})).toThrow("NEXT_PUBLIC_API_URL is required");
  });

  it("returns a normalized env object", () => {
    expect(
      loadClientEnv({
        NEXT_PUBLIC_API_URL: "http://localhost:8000",
      }),
    ).toEqual({
      NEXT_PUBLIC_API_URL: "http://localhost:8000",
    });
  });
});
