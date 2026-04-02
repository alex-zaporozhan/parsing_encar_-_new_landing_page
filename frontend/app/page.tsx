import { VehicleCatalog } from "@/components/VehicleCatalog";

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <header className="border-b border-neutral-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-4 py-10 sm:px-6 lg:px-8">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">
            Демо-каталог
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            Подборка с ENCAR
          </h1>
          <p className="max-w-2xl text-sm leading-relaxed text-ink-muted sm:text-base">
            Карточки обновляются по расписанию. Кнопка ведёт на оригинальное объявление на
            encar.com.
          </p>
        </div>
      </header>
      <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <VehicleCatalog />
      </section>
      <footer className="border-t border-neutral-200 py-8 text-center text-xs text-ink-muted">
        Данные: публичный API encar.com · не аффилировано с ENCAR
      </footer>
    </main>
  );
}
