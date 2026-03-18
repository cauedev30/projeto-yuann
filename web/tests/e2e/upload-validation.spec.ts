import { expect, test } from "@playwright/test";

test("operator cannot submit the intake flow until a file is attached, then completes the upload", async ({
  page,
}) => {
  await page.goto("/contracts");

  const submitButton = page.getByRole("button", { name: "Enviar contrato" });

  await expect(page.locator("span", { hasText: "Aguardando envio" })).toBeVisible();
  await expect(submitButton).toBeDisabled();

  await page.getByLabel("Titulo do contrato").fill("Loja Validacao");
  await page.getByLabel("Referencia externa").fill("LOC-E2E-VALID");

  await expect(submitButton).toBeDisabled();
  await expect(page.locator("span", { hasText: "Aguardando envio" })).toBeVisible();

  await page.getByLabel("Contrato PDF").setInputFiles("tests/fixtures/third-party-draft.pdf");
  await expect(submitButton).toBeEnabled();
  await submitButton.click();

  await expect(page.locator("span", { hasText: "Triagem concluida" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Findings principais" })).toBeVisible();
});
