import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";

import { expect, test } from "@playwright/test";

const backendDir = path.resolve(process.cwd(), "../backend");
const runtimeSeedScript = path.join("tests", "support", "seed_dashboard_runtime.py");

function resolveBackendPython(): string {
  const windowsVenvPython = path.join(backendDir, ".venv", "Scripts", "python.exe");
  const windowsSharedVenvPython = path.resolve(
    backendDir,
    "..",
    "..",
    "..",
    "backend",
    ".venv",
    "Scripts",
    "python.exe",
  );
  const unixVenvPython = path.join(backendDir, ".venv", "bin", "python");
  const unixSharedVenvPython = path.resolve(
    backendDir,
    "..",
    "..",
    "..",
    "backend",
    ".venv",
    "bin",
    "python",
  );

  if (process.platform === "win32") {
    const windowsSystemPython = process.env.LOCALAPPDATA
      ? path.join(process.env.LOCALAPPDATA, "Programs", "Python", "Python313", "python.exe")
      : "";

    if (existsSync(windowsVenvPython)) {
      return windowsVenvPython;
    }
    if (existsSync(windowsSharedVenvPython)) {
      return windowsSharedVenvPython;
    }
    if (windowsSystemPython && existsSync(windowsSystemPython)) {
      return windowsSystemPython;
    }
    return "python";
  }

  if (existsSync(unixVenvPython)) {
    return unixVenvPython;
  }
  if (existsSync(unixSharedVenvPython)) {
    return unixSharedVenvPython;
  }
  return "python3";
}

function prepareDashboardRuntime(mode: "clear" | "seed") {
  execFileSync(resolveBackendPython(), [runtimeSeedScript, mode], {
    cwd: backendDir,
    stdio: "pipe",
  });
}

test.beforeEach(() => {
  prepareDashboardRuntime("clear");
});

test("operator reviews notification history with recipients, statuses, channel, and contract context", async ({
  page,
}) => {
  prepareDashboardRuntime("seed");

  await page.goto("/dashboard");
  const historyCard = page
    .getByRole("heading", { name: "Historico de notificacoes" })
    .locator("xpath=ancestor::section[1]");

  await expect(page.getByText("Historico de notificacoes")).toBeVisible();
  await expect(historyCard.getByText("finance@example.com")).toBeVisible();
  await expect(historyCard.getByText("Enviado", { exact: true })).toBeVisible();
  await expect(historyCard.getByText("Pendente", { exact: true })).toBeVisible();
  await expect(historyCard.locator("p").filter({ hasText: /· email ·/ }).first()).toBeVisible();
  await expect(historyCard.locator("strong").first()).toContainText(/Loja/);
});
