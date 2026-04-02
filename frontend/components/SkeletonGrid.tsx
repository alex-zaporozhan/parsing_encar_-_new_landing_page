export function SkeletonGrid() {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-sm"
        >
          <div className="aspect-[4/3] animate-pulse bg-neutral-200" />
          <div className="space-y-3 p-4">
            <div className="h-4 w-3/4 animate-pulse rounded bg-neutral-200" />
            <div className="h-3 w-1/2 animate-pulse rounded bg-neutral-200" />
            <div className="h-8 w-full animate-pulse rounded-xl bg-neutral-200" />
          </div>
        </div>
      ))}
    </div>
  );
}
