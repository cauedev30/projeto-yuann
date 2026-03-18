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

test("operator completes the full release journey from intake to operational dashboard", async ({
  page,
}) => {
  prepareDashboardRuntime("seed");

  await page.goto("/contracts");
  await page.getByLabel("Titulo do contrato").fill("Loja E2E Full");
  await page.getByLabel("Referencia externa").fill("LOC-E2E-FULL");
  await page.getByLabel("Contrato PDF").setInputFiles("tests/fixtures/third-party-draft.pdf");
  await page.getByRole("button", { name: "Enviar contrato" }).click();

  await expect(page.getByRole("heading", { name: "Findings principais" })).toBeVisible();
  await expect(page.getByText("Prazo de vigencia", { exact: true })).toBeVisible();
  await expect(page.getByText("Critico", { exact: true })).toBeVisible();
  await expect(page.locator("span", { hasText: "Triagem concluida" })).toBeVisible();

  const contractLink = page.getByRole("link", { name: /LOC-E2E-FULL/i });
  await expect(contractLink).toBeVisible();
  await Promise.all([
    page.waitForURL(/\/contracts\/.+/, { timeout: 15000 }),
    contractLink.click(),
  ]);

  await expect(page.getByRole("heading", { name: "Loja E2E Full" })).toBeVisible();
  await expect(page.getByText("third-party-draft.pdf")).toBeVisible();

  await Promise.all([
    page.waitForURL(/\/dashboard$/, { timeout: 15000 }),
    page.getByRole("link", { name: "Dashboard" }).click(),
  ]);

  await expect(page.getByText("Resumo do portifolio")).toBeVisible();
  await expect(page.getByText("Contratos ativos")).toBeVisible();
  await expect(page.getByText("Timeline de eventos")).toBeVisible();
  await expect(page.getByText("Historico de notificacoes")).toBeVisible();
  await expect(page.getByText("finance@example.com")).toBeVisible();
});
