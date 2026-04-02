import Image from "next/image";
import type { VehicleDTO } from "@/lib/types";

function formatKrw(amount: number): string {
  return new Intl.NumberFormat("ko-KR", {
    style: "currency",
    currency: "KRW",
    maximumFractionDigits: 0,
  }).format(amount);
}

type Props = { vehicle: VehicleDTO };

export function VehicleCard({ vehicle }: Props) {
  const title = `${vehicle.make} ${vehicle.model}`.trim();
  const photo = vehicle.photos?.[0];
  const mileageLabel =
    vehicle.mileage_km != null
      ? `${vehicle.mileage_km.toLocaleString("ru-RU")} км`
      : "—";

  return (
    <article className="group flex flex-col overflow-hidden rounded-2xl border border-neutral-200/80 bg-white shadow-sm transition hover:border-neutral-300 hover:shadow-md">
      <div className="relative aspect-[4/3] bg-neutral-100">
        {photo ? (
          <Image
            src={photo}
            alt={title}
            fill
            className="object-cover transition duration-300 group-hover:scale-[1.02]"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-neutral-400">
            Нет фото
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-2 p-4">
        <h2
          className="line-clamp-2 text-base font-semibold leading-snug text-ink"
          title={title}
        >
          {title}
        </h2>
        <div className="flex flex-wrap gap-x-3 gap-y-1 text-sm text-ink-muted">
          <span>{vehicle.year}</span>
          <span className="text-neutral-300">·</span>
          <span title={`Пробег: ${mileageLabel}`}>{mileageLabel}</span>
        </div>
        <p className="text-lg font-semibold tracking-tight text-ink">
          {formatKrw(vehicle.price.amount)}
        </p>
        <div className="mt-auto space-y-1.5 pt-2">
          {vehicle.source_url ? (
            <>
              <a
                href={vehicle.source_url}
                target="_blank"
                rel="noopener"
                data-testid="encar-cta"
                className="inline-flex w-full items-center justify-center rounded-xl bg-ink px-4 py-3 text-sm font-semibold text-white transition hover:bg-neutral-800 active:scale-[0.99]"
              >
                Смотреть на ENCAR
              </a>
              <p className="text-center text-xs leading-snug text-neutral-500">
                Откроется официальная карточка на encar.com (поддомен fem).
              </p>
            </>
          ) : (
            <button
              type="button"
              disabled
              title="Ссылка на объявление недоступна"
              className="inline-flex w-full cursor-not-allowed items-center justify-center rounded-xl bg-ink px-4 py-3 text-sm font-semibold text-white opacity-40"
            >
              Смотреть на ENCAR
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
