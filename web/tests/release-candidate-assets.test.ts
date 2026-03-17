import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

const repoRoot = path.resolve(process.cwd(), "..");
const fixtureDir = path.join(process.cwd(), "tests", "fixtures");

describe("release candidate assets", () => {
  it("tracks a readable draft contract fixture for the demo flow", () => {
    const fixturePath = path.join(fixtureDir, "third-party-draft.pdf");

    expect(existsSync(fixturePath)).toBe(true);
    expect(readFileSync(fixturePath, "latin1").startsWith("%PDF-")).toBe(true);
  });

  it("keeps the invalid upload fixture used by the demo flow", () => {
    const fixturePath = path.join(fixtureDir, "unreadable-upload.pdf");

    expect(existsSync(fixturePath)).toBe(true);
  });

  it("exposes explicit dashboard seed targets in the Makefile", () => {
    const makefile = readFileSync(path.join(repoRoot, "Makefile"), "utf8");

    expect(makefile).toContain("release-seed-dashboard:");
    expect(makefile).toContain("release-clear-dashboard:");
  });

  it("documents the seed command and demo fixtures in release docs", () => {
    const readme = readFileSync(path.join(repoRoot, "README.md"), "utf8");
    const runbook = readFileSync(
      path.join(repoRoot, "docs", "release-candidate-runbook.md"),
      "utf8",
    );

    expect(readme).toContain("py -3.13 -m tests.support.seed_dashboard_runtime seed");
    expect(readme).toContain("tests/fixtures/third-party-draft.pdf");
    expect(runbook).toContain("py -3.13 -m tests.support.seed_dashboard_runtime seed");
    expect(runbook).toContain("py -3.13 -m tests.support.seed_dashboard_runtime clear");
    expect(runbook).toContain("tests/fixtures/third-party-draft.pdf");
  });
});
