import { expect, test } from "@playwright/test";
import { isApiUp } from "./helpers";

const API = process.env.E2E_API_URL ?? "http://127.0.0.1:8000";

test("CORS preflight OPTIONS (MR-1)", async ({ request }) => {
  test.skip(!(await isApiUp(request)), "API :8000 недоступен");
  const r = await request.fetch(`${API}/api/v1/vehicles?limit=1`, {
    method: "OPTIONS",
    headers: {
      Origin: "http://localhost:3000",
      "Access-Control-Request-Method": "GET",
    },
  });
  expect(r.status()).toBeLessThan(500);
  const origin = r.headers()["access-control-allow-origin"];
  expect(origin).toBeTruthy();
});
