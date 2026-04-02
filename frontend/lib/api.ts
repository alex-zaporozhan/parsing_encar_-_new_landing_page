import type { VehiclesResponse } from "./types";

/** Совпадает с лимитом ARCH (max 200); страницы грузим порциями. */
export const VEHICLES_PAGE_SIZE = 50;

export function getApiBase(): string {
  const u = process.env.NEXT_PUBLIC_API_URL;
  if (u && u.length > 0) return u.replace(/\/$/, "");
  return "http://127.0.0.1:8000";
}

export async function fetchVehiclesPage(
  offset: number,
  limit: number,
  signal?: AbortSignal,
): Promise<VehiclesResponse> {
  const base = getApiBase();
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  const res = await fetch(`${base}/api/v1/vehicles?${params}`, {
    signal,
    cache: "no-store",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail =
      typeof err?.detail === "string" ? err.detail : res.statusText;
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json() as Promise<VehiclesResponse>;
}

/** Первая страница (обратная совместимость для тестов/импортов). */
export async function fetchVehicles(
  signal?: AbortSignal,
): Promise<VehiclesResponse> {
  return fetchVehiclesPage(0, VEHICLES_PAGE_SIZE, signal);
}
