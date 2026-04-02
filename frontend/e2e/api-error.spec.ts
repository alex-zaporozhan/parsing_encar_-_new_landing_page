import { expect, test } from "@playwright/test";

/**
 * MR-3 / MR-5: UI при ошибке API (мок 500 с контрактом).
 */
test("ошибка API: сообщение и «Повторить»", async ({ page }) => {
  await page.route("**/api/v1/vehicles**", async (route) => {
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({
        detail: "Database error",
        code: "INTERNAL_ERROR",
      }),
    });
  });

  await page.goto("/");
  await expect(page.getByText(/Database error|Ошибка/i)).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByRole("button", { name: "Повторить" })).toBeVisible();
});
