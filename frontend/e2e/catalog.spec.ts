import { expect, test } from "@playwright/test";
import { isApiUp } from "./helpers";

test.describe("ENCAR landing (браузер)", () => {
  test("главная: нет горизонтального скролла на узкой ширине (MR-4)", async ({
    page,
    request,
  }) => {
    test.skip(
      !(await isApiUp(request)),
      "Запустите API: uvicorn на :8000",
    );
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/");
    await page.waitForLoadState("domcontentloaded");
    await expect(
      page.getByTestId("catalog-loaded").or(page.getByTestId("catalog-empty")),
    ).toBeVisible({ timeout: 30_000 });
    const overflow = await page.evaluate(() => {
      const el = document.documentElement;
      return el.scrollWidth > el.clientWidth;
    });
    expect(overflow, "нет лишнего горизонтального скролла").toBe(false);
  });

  test("после загрузки — catalog-loaded или catalog-empty", async ({
    page,
    request,
  }) => {
    test.skip(!(await isApiUp(request)), "API :8000 недоступен");
    await page.goto("/");
    await expect(
      page.getByTestId("catalog-loaded").or(page.getByTestId("catalog-empty")),
    ).toBeVisible({ timeout: 30_000 });
  });

  test("ссылка ENCAR ведёт на encar.com", async ({ page, request }) => {
    test.skip(!(await isApiUp(request)), "API :8000 недоступен");
    await page.goto("/");
    await expect(
      page.getByTestId("catalog-loaded").or(page.getByTestId("catalog-empty")),
    ).toBeVisible({ timeout: 30_000 });
    if (await page.getByTestId("catalog-empty").isVisible().catch(() => false)) {
      test.skip(true, "Пустая БД");
      return;
    }
    const loaded = page.getByTestId("catalog-loaded");
    const link = page.getByTestId("encar-cta").first();
    await expect(link).toBeVisible();
    const href = await link.getAttribute("href");
    expect(href).toMatch(/^https:\/\/.+\.encar\.com\//i);
  });

  test("«Показать ещё» при большом каталоге (MR-6)", async ({
    page,
    request,
  }) => {
    test.skip(!(await isApiUp(request)), "API :8000 недоступен");
    await page.goto("/");
    const more = page.getByTestId("load-more");
    if (!(await more.isVisible().catch(() => false))) {
      test.skip(true, "Одна страница данных или пусто");
      return;
    }
    await more.click();
    await expect(more).toBeEnabled({ timeout: 20_000 });
  });
});
