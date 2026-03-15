import { expect, test } from "@playwright/test";

test("operator reviews the dashboard timeline and notification history", async ({ page }) => {
  await page.goto("/dashboard");

  await expect(page.getByText("Timeline de eventos")).toBeVisible();
  await expect(page.getByText("renewal")).toBeVisible();
  await expect(page.getByText("alerts@example.com")).toBeVisible();
});
