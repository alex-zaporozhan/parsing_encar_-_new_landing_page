import type { APIRequestContext } from "@playwright/test";

const API = process.env.E2E_API_URL ?? "http://127.0.0.1:8000";

export async function isApiUp(request: APIRequestContext): Promise<boolean> {
  try {
    const r = await request.get(`${API}/api/v1/health`, { timeout: 5_000 });
    return r.ok();
  } catch {
    return false;
  }
}
