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
  const windowsSystemPython = process.env.LOCALAPPDATA
    ? path.join(process.env.LOCALAPPDATA, "Programs", "Python", "Python313", "python.exe")
    : "";
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

test("operator sees an honest unavailable dashboard state before runtime data is integrated", async ({ page }) => {
  await page.goto("/dashboard");

  await expect(page.getByText("Governanca contratual em andamento")).toBeVisible();
  await expect(page.getByText("Dashboard indisponivel no momento.")).toBeVisible();
});

test("operator sees the populated dashboard, filters the timeline, and keeps full alert history", async ({
  page,
}) => {
  prepareDashboardRuntime("seed");

  await page.goto("/dashboard");

  await expect(page.getByText("Resumo do portifolio")).toBeVisible();
  await expect(page.getByText("Contratos ativos")).toBeVisible();
  await expect(page.getByText("Findings criticos")).toBeVisible();
  await expect(page.getByText("Vencendo em 12 meses")).toBeVisible();
  await expect(page.getByText("finance@example.com")).toBeVisible();
  await expect(page.getByText("Loja Centro", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Loja Norte", { exact: true }).first()).toBeVisible();

  await page.getByRole("button", { name: "Vencidos" }).click();
  await expect(page.getByText("Atrasado ha 5 dias")).toBeVisible();
  await expect(page.getByText("Dentro da janela de alerta (30 dias)")).not.toBeVisible();

  await page.getByRole("button", { name: "Na janela" }).click();
  await expect(page.getByText("Dentro da janela de alerta (30 dias)")).toBeVisible();
  await expect(page.getByText("Atrasado ha 5 dias")).not.toBeVisible();
});
