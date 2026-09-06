import { Skeleton } from "@/components/ui/skeleton";

/** Mirrors the real card composition (tall top row, medium middle row, one
 * full-width card) instead of a single centered spinner. */
export function StatisticsSkeleton() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Skeleton className="h-[300px] rounded-2xl lg:h-[340px] lg:col-span-1" />
        <Skeleton className="h-[300px] rounded-2xl lg:h-[340px] lg:col-span-2" />
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Skeleton className="h-[160px] rounded-2xl" />
        <Skeleton className="h-[160px] rounded-2xl" />
        <Skeleton className="h-[160px] rounded-2xl" />
      </div>
      <Skeleton className="h-[220px] rounded-2xl" />
    </div>
  );
}
