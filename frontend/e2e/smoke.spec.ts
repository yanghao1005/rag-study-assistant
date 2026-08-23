import { expect, test } from "@playwright/test";

test("landing smoke", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Studyraft" })).toBeVisible();
});

test("login smoke", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByText("Studyraft").first()).toBeVisible();
  await expect(page.locator("#email")).toBeVisible();
});
