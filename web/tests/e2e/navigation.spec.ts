import { expect, test } from "@playwright/test";

test("operator navigates through the mobile workspace menu", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto("/dashboard");

  await expect(page.locator("aside")).not.toBeVisible();

  await page.getByText("Abrir navegacao").click();
  await Promise.all([
    page.waitForURL(/\/contracts$/, { timeout: 15000 }),
    page.getByRole("link", { name: "Contracts" }).click(),
  ]);

  await expect(page.getByRole("heading", { name: "Upload do contrato" })).toBeVisible();
});
