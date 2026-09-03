"use client";

import { cn } from "@/lib/utils";
import { ASPECT_RATIO_LABELS } from "../lib/labels";
import type { DesignAspectRatio } from "../types/design";

// Tailwind class per ratio for the little proportion swatch - kept as a
// static lookup (not computed) so the aspect-* classes survive purging.
const SWATCH_ASPECT_CLASS: Record<DesignAspectRatio, string> = {
  "1:1": "aspect-square w-5",
  "4:5": "aspect-[4/5] w-4",
  "16:9": "aspect-video w-7",
  "9:16": "aspect-[9/16] w-3",
};

type AspectRatioSelectProps = {
  value: DesignAspectRatio;
  onChange: (ratio: DesignAspectRatio) => void;
  /** Part 35: a template must not blindly stretch into a ratio it was
   * never designed for - only the selected template's own supported list
   * is offered here, never all four unconditionally. */
  allowed: DesignAspectRatio[];
  disabled?: boolean;
};

export function AspectRatioSelect({ value, onChange, allowed, disabled }: AspectRatioSelectProps) {
  return (
    <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4" role="radiogroup" aria-label="اختر أبعاد التصميم">
      {allowed.map((ratio) => {
        const active = value === ratio;
        return (
          <button
            key={ratio}
            type="button"
            role="radio"
            aria-checked={active}
            disabled={disabled}
            onClick={() => onChange(ratio)}
            className={cn(
              "flex flex-col items-center gap-2 rounded-2xl border px-3 py-4 text-center transition-all disabled:pointer-events-none disabled:opacity-50",
              active
                ? "border-transparent bg-[image:var(--gradient-primary)] text-white shadow-[0_10px_24px_-10px_rgba(27,143,234,0.55)]"
                : "border-border bg-white text-foreground hover:border-[#1B8FEA]/40 hover:bg-secondary/40",
            )}
          >
            <span
              className={cn(
                "rounded-[3px] border-2",
                SWATCH_ASPECT_CLASS[ratio],
                active ? "border-white/80" : "border-current opacity-60",
              )}
              aria-hidden="true"
            />
            <span className="flex flex-col leading-tight">
              <span className="text-sm font-medium">{ASPECT_RATIO_LABELS[ratio]}</span>
              <span className={cn("text-[11px]", active ? "text-white/80" : "text-muted-foreground")}>
                {ratio}
              </span>
            </span>
          </button>
        );
      })}
    </div>
  );
}
