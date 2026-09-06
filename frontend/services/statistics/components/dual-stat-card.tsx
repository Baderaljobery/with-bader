import type { LucideIcon } from "lucide-react";

import { formatCount } from "../lib/format";
import { STAT_THEME, type StatTone } from "../lib/theme";

type Stat = {
  label: string;
  value: number;
};

type DualStatCardProps = {
  tone: StatTone;
  icon: LucideIcon;
  title: string;
  primary: Stat;
  secondary: Stat;
};

/** Two closely-related counts shown as peers (e.g. scheduled/completed
 * interviews) rather than a hero + footnote - used for the three medium
 * cards below the top row. */
export function DualStatCard({ tone, icon: Icon, title, primary, secondary }: DualStatCardProps) {
  const colors = STAT_THEME[tone];

  return (
    <div
      className="flex flex-col gap-4 rounded-2xl p-5 shadow-[var(--shadow-soft)]"
      style={{ backgroundColor: colors.background }}
    >
      <div className="flex items-center gap-2.5">
        <span
          className="flex size-8 shrink-0 items-center justify-center rounded-full"
          style={{ backgroundColor: "rgba(255,255,255,0.7)" }}
        >
          <Icon className="size-4" aria-hidden="true" style={{ color: colors.accent }} />
        </span>
        <p className="text-sm font-medium" style={{ color: colors.text }}>
          {title}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {[primary, secondary].map((stat) => (
          <div key={stat.label} className="rounded-xl bg-white/60 px-3 py-2.5">
            <p className="font-heading text-2xl font-bold tracking-tight" style={{ color: colors.text }}>
              {formatCount(stat.value)}
            </p>
            <p className="mt-0.5 text-[11px]" style={{ color: colors.subtleText }}>
              {stat.label}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
