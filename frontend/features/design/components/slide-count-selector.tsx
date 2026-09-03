"use client";

import { cn } from "@/lib/utils";

const COUNTS = [1, 2, 3, 4, 5] as const;

type SlideCountSelectorProps = {
  value: number;
  onChange: (count: number) => void;
  disabled?: boolean;
};

/** Exactly 1-5, always a manual choice - never inferred (Part 3). */
export function SlideCountSelector({ value, onChange, disabled }: SlideCountSelectorProps) {
  return (
    <div
      role="radiogroup"
      aria-label="عدد الشرائح"
      className="inline-flex gap-1 rounded-2xl border border-border bg-secondary/40 p-1.5"
    >
      {COUNTS.map((count) => {
        const active = value === count;
        return (
          <button
            key={count}
            type="button"
            role="radio"
            aria-checked={active}
            disabled={disabled}
            onClick={() => onChange(count)}
            className={cn(
              "flex size-10 items-center justify-center rounded-xl text-sm font-semibold transition-all disabled:pointer-events-none disabled:opacity-50",
              active
                ? "bg-white text-foreground shadow-[var(--shadow-soft)]"
                : "text-muted-foreground hover:bg-white/70 hover:text-foreground",
            )}
          >
            {count}
          </button>
        );
      })}
    </div>
  );
}
