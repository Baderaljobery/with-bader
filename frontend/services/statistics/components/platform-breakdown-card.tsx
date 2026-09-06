"use client";

import { Layers } from "lucide-react";

import { PLATFORM_ICONS, PLATFORM_LABELS } from "@/services/content/lib/labels";
import { formatCount } from "../lib/format";
import type { PlatformCount } from "../types/statistics";

type PlatformBreakdownCardProps = {
  platforms: PlatformCount[];
};

/** Compact segmented horizontal bars, sorted by volume - no legend needed
 * since each row already carries its own label. */
export function PlatformBreakdownCard({ platforms }: PlatformBreakdownCardProps) {
  const sorted = [...platforms].sort((a, b) => b.count - a.count);
  const max = Math.max(1, ...sorted.map((row) => row.count));
  const total = sorted.reduce((sum, row) => sum + row.count, 0);

  return (
    <div
      className="rounded-2xl border border-border p-5 shadow-[var(--shadow-soft)]"
      style={{ backgroundImage: "var(--surface-tint)" }}
    >
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium text-foreground">المحتوى حسب المنصة</p>
        <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-secondary">
          <Layers className="size-4 text-muted-foreground" aria-hidden="true" />
        </span>
      </div>

      {total === 0 ? (
        <div className="mt-4 flex items-center justify-center rounded-xl border border-dashed border-border py-8 text-center text-sm text-muted-foreground">
          لا توجد بيانات كافية بعد
        </div>
      ) : (
        <div className="mt-4 space-y-3">
          {sorted.map((row) => {
            const Icon = PLATFORM_ICONS[row.platform];
            const widthPercent = (row.count / max) * 100;
            return (
              <div key={row.platform} className="flex items-center gap-3">
                <div className="flex w-24 shrink-0 items-center gap-1.5">
                  <Icon className="size-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
                  <span className="truncate text-xs font-medium text-foreground">
                    {PLATFORM_LABELS[row.platform]}
                  </span>
                </div>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${widthPercent}%`, backgroundImage: "var(--gradient-primary)" }}
                  />
                </div>
                <span className="w-8 shrink-0 text-end text-xs font-semibold text-foreground">
                  {formatCount(row.count)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
