"use client";

import { TrendingUp } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, Tooltip } from "recharts";

import { cn } from "@/lib/utils";
import { formatCount, formatShortDayMonth } from "../lib/format";
import type { ActivityPoint } from "../types/statistics";

type ActivityTrendCardProps = {
  activity: ActivityPoint[];
  className?: string;
};

function ActivityTooltip({ active, payload }: { active?: boolean; payload?: { payload: ActivityPoint }[] }) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return (
    <div className="rounded-lg border border-border bg-white px-2.5 py-1.5 text-xs shadow-[var(--shadow-soft)]">
      <p className="font-medium text-foreground">{formatCount(point.count)} نشاط</p>
      <p className="text-muted-foreground">{formatShortDayMonth(point.date)}</p>
    </div>
  );
}

/** A single smooth area - no visible axes/gridlines/legend, the chart is
 * meant to read as texture inside the card, not a standalone graph. */
export function ActivityTrendCard({ activity, className }: ActivityTrendCardProps) {
  const total = activity.reduce((sum, point) => sum + point.count, 0);
  const last7 = activity.slice(-7).reduce((sum, point) => sum + point.count, 0);

  return (
    <div
      className={cn("flex flex-col gap-4 rounded-2xl border border-border p-5 shadow-[var(--shadow-soft)]", className)}
      style={{ backgroundImage: "var(--surface-tint)" }}
    >
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-foreground">النشاط خلال آخر 30 يومًا</p>
          <p className="mt-1 font-heading text-3xl font-bold tracking-tight text-foreground">
            {formatCount(total)}
          </p>
          <p className="mt-1 text-xs text-muted-foreground">{formatCount(last7)} خلال آخر 7 أيام</p>
        </div>
        <span
          className="flex size-9 shrink-0 items-center justify-center rounded-full"
          style={{ backgroundImage: "var(--gradient-primary)" }}
        >
          <TrendingUp className="size-4.5 text-white" aria-hidden="true" />
        </span>
      </div>

      {total === 0 ? (
        <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-border py-10 text-center text-sm text-muted-foreground">
          لا توجد بيانات كافية بعد
        </div>
      ) : (
        <div className="-mx-2 h-32 flex-1 sm:h-full sm:min-h-[140px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={activity} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
              <defs>
                <linearGradient id="activityFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#1FCFC3" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#1B8FEA" stopOpacity={0.02} />
                </linearGradient>
                <linearGradient id="activityStroke" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#1FCFC3" />
                  <stop offset="100%" stopColor="#1B8FEA" />
                </linearGradient>
              </defs>
              <Tooltip content={<ActivityTooltip />} cursor={{ stroke: "#E6EAF0" }} />
              <Area
                type="monotone"
                dataKey="count"
                stroke="url(#activityStroke)"
                strokeWidth={2.5}
                fill="url(#activityFill)"
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
