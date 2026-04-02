"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  fetchVehiclesPage,
  VEHICLES_PAGE_SIZE,
} from "@/lib/api";
import type { VehicleDTO } from "@/lib/types";
import { SkeletonGrid } from "./SkeletonGrid";
import { VehicleCard } from "./VehicleCard";

export function VehicleCatalog() {
  const [items, setItems] = useState<VehicleDTO[] | null>(null);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadMoreError, setLoadMoreError] = useState<string | null>(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  const loadInitial = useCallback(async (signal?: AbortSignal) => {
    if (!mounted.current) return;
    setLoading(true);
    setError(null);
    setLoadMoreError(null);
    try {
      const data = await fetchVehiclesPage(0, VEHICLES_PAGE_SIZE, signal);
      if (!mounted.current) return;
      setItems(data.items);
      setTotal(data.total);
    } catch (e) {
      if ((e as Error).name === "AbortError") return;
      if (!mounted.current) return;
      setError((e as Error).message || "Ошибка загрузки");
    } finally {
      if (mounted.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    const ac = new AbortController();
    void loadInitial(ac.signal);
    return () => ac.abort();
  }, [loadInitial]);

  const loadMore = useCallback(async () => {
    if (!items || items.length >= total || loadingMore) return;
    setLoadingMore(true);
    setLoadMoreError(null);
    try {
      const data = await fetchVehiclesPage(
        items.length,
        VEHICLES_PAGE_SIZE,
      );
      if (!mounted.current) return;
      setItems((prev) => [...(prev ?? []), ...data.items]);
    } catch (e) {
      if (!mounted.current) return;
      setLoadMoreError(
        (e as Error).message || "Не удалось подгрузить объявления",
      );
    } finally {
      if (mounted.current) setLoadingMore(false);
    }
  }, [items, total, loadingMore]);

  if (loading) {
    return <SkeletonGrid />;
  }

  if (error) {
    return (
      <div
        className="rounded-2xl border border-red-200 bg-red-50 px-6 py-10 text-center"
        data-testid="catalog-error"
      >
        <p className="text-red-800">{error}</p>
        <button
          type="button"
          onClick={() => void loadInitial()}
          disabled={loading}
          className="mt-4 rounded-xl bg-ink px-5 py-2.5 text-sm font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Повторить
        </button>
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div
        className="rounded-2xl border border-dashed border-neutral-300 bg-white px-6 py-16 text-center"
        data-testid="catalog-empty"
      >
        <p className="text-lg font-medium text-ink">Пока нет объявлений</p>
        <p className="mt-2 text-sm text-ink-muted">
          Запустите обновление каталога на сервере (cron или{" "}
          <code className="rounded bg-neutral-100 px-1.5 py-0.5 text-xs">
            python -m app.jobs.fetch_encar
          </code>
          ), затем обновите список.
        </p>
        <button
          type="button"
          onClick={() => void loadInitial()}
          disabled={loading}
          className="mt-6 inline-flex w-full max-w-xs items-center justify-center rounded-xl bg-ink px-6 py-3 text-sm font-semibold text-white transition hover:bg-neutral-800 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
        >
          Обновить список
        </button>
      </div>
    );
  }

  const hasMore = items.length < total;
  const remaining = Math.max(0, total - items.length);

  return (
    <div data-testid="catalog-loaded">
      {loadMoreError && (
        <p
          className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
          role="alert"
        >
          {loadMoreError}{" "}
          <button
            type="button"
            onClick={() => void loadMore()}
            className="font-semibold underline underline-offset-2 hover:text-amber-950"
          >
            Повторить
          </button>
        </p>
      )}
      <p className="mb-6 text-sm text-ink-muted">
        Показано {items.length} из {total}
      </p>
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {items.map((v) => (
          <VehicleCard key={v.id} vehicle={v} />
        ))}
      </div>
      {hasMore && (
        <div className="mt-10 flex flex-col items-center gap-3">
          <button
            type="button"
            onClick={() => void loadMore()}
            disabled={loadingMore}
            data-testid="load-more"
            className="rounded-xl border border-neutral-300 bg-white px-6 py-3 text-sm font-semibold text-ink transition hover:border-neutral-400 hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loadingMore
              ? "Загрузка…"
              : `Показать ещё (${remaining})`}
          </button>
        </div>
      )}
    </div>
  );
}
