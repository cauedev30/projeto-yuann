import { expect, test } from "@playwright/test";

test("operator sees an honest unavailable dashboard state before runtime data is integrated", async ({ page }) => {
  await page.goto("/dashboard");

  await expect(page.getByText("Dashboard de renovacoes")).toBeVisible();
  await expect(page.getByText("Dashboard indisponivel no momento.")).toBeVisible();
});
