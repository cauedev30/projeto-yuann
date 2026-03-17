import { expect, test } from "@playwright/test";

test("operator opens a persisted contract from the real list and reaches the real detail route", async ({
  page,
}) => {
  const uniqueSuffix = Date.now().toString();
  const contractTitle = `Loja Centro ${uniqueSuffix}`;
  const externalReference = `LOC-E2E-${uniqueSuffix}`;

  await page.goto("/contracts");
  await page.getByLabel("Titulo do contrato").fill(contractTitle);
  await page.getByLabel("Referencia externa").fill(externalReference);
  await page.getByLabel("Contrato PDF").setInputFiles("tests/fixtures/third-party-draft.pdf");
  await page.getByRole("button", { name: "Enviar contrato" }).click();

  const contractLink = page.getByRole("link", { name: new RegExp(externalReference) });
  await expect(contractLink).toBeVisible();
  await Promise.all([
    page.waitForURL(/\/contracts\/.+/, { timeout: 15000 }),
    contractLink.click(),
  ]);

  await expect(page.getByRole("heading", { name: contractTitle })).toBeVisible();
  await expect(page.getByText("third-party-draft.pdf")).toBeVisible();
  await expect(page.getByText("Analise ainda nao disponivel.")).toBeVisible();
});
