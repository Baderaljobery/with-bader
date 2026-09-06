import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";
import { formatCount } from "../lib/format";
import { STAT_THEME, type StatTone } from "../lib/theme";

type MetricCardProps = {
  tone: StatTone;
  icon: LucideIcon;
  title: string;
  value: number;
  valueLabel: string;
  secondary?: { icon: LucideIcon; label: string; value: number };
  className?: string;
  children?: ReactNode;
};

/** The single-headline KPI card shell - a dominant number, a short label,
 * an optional small secondary stat, and room for an embedded chart
 * (`children`) so charts feel built into the card rather than bolted on. */
export function MetricCard({
  tone,
  icon: Icon,
  title,
  value,
  valueLabel,
  secondary,
  className,
  children,
}: MetricCardProps) {
  const colors = STAT_THEME[tone];
  const isDark = tone === "navy";

  return (
    <div
      className={cn("flex flex-col gap-4 rounded-2xl p-5 shadow-[var(--shadow-soft)]", className)}
      style={{ backgroundColor: colors.background }}
    >
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium" style={{ color: isDark ? colors.subtleText : colors.text }}>
          {title}
        </p>
        <span
          className="flex size-9 shrink-0 items-center justify-center rounded-full"
          style={{ backgroundColor: isDark ? "rgba(255,255,255,0.1)" : "rgba(255,255,255,0.7)" }}
        >
          <Icon className="size-4.5" aria-hidden="true" style={{ color: colors.accent }} />
        </span>
      </div>

      <div>
        <p className="font-heading text-4xl font-bold tracking-tight" style={{ color: colors.text }}>
          {formatCount(value)}
        </p>
        <p className="mt-1 text-xs" style={{ color: colors.subtleText }}>
          {valueLabel}
        </p>
      </div>

      {secondary ? (
        <div
          className="flex items-center gap-2 rounded-xl px-3 py-2"
          style={{ backgroundColor: isDark ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.6)" }}
        >
          <secondary.icon className="size-4 shrink-0" aria-hidden="true" style={{ color: colors.accent }} />
          <span className="text-xs" style={{ color: isDark ? colors.subtleText : colors.text }}>
            {secondary.label}
          </span>
          <span className="ms-auto text-sm font-semibold" style={{ color: colors.text }}>
            {formatCount(secondary.value)}
          </span>
        </div>
      ) : null}

      {children}
    </div>
  );
}
