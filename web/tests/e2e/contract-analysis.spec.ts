import { expect, test } from "@playwright/test";

test("operator uploads a contract and reviews the findings", async ({ page }) => {
  await page.goto("/contracts");
  await page.getByLabel("Titulo do contrato").fill("Loja Centro");
  await page.getByLabel("Referencia externa").fill("LOC-001");
  await page.getByLabel("Contrato PDF").setInputFiles("tests/fixtures/third-party-draft.pdf");
  await page.getByRole("button", { name: "Enviar contrato" }).click();

  await expect(page.getByRole("heading", { name: "Findings principais" })).toBeVisible();
  await expect(page.getByText("Prazo de vigencia", { exact: true })).toBeVisible();
  await expect(page.getByText("Critico", { exact: true })).toBeVisible();
});

test("operator sees a readable error for an unreadable pdf upload", async ({ page }) => {
  await page.goto("/contracts");
  await page.getByLabel("Titulo do contrato").fill("Loja Centro");
  await page.getByLabel("Referencia externa").fill("LOC-ERR-001");
  await page.getByLabel("Contrato PDF").setInputFiles("tests/fixtures/unreadable-upload.pdf");
  await page.getByRole("button", { name: "Enviar contrato" }).click();

  await expect(page.locator("p[role='alert']")).toContainText(
    "O arquivo enviado nao e um PDF legivel.",
  );
});
