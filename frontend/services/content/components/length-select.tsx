"use client";

import { cn } from "@/lib/utils";
import { LENGTH_LABELS } from "../lib/labels";
import type { ContentLength } from "../types/content";

const LENGTHS: ContentLength[] = ["short", "medium", "detailed"];

type LengthSelectProps = {
  value: ContentLength;
  onChange: (length: ContentLength) => void;
  disabled?: boolean;
};

export function LengthSelect({ value, onChange, disabled }: LengthSelectProps) {
  return (
    <div
      role="radiogroup"
      aria-label="اختر طول المحتوى"
      className="inline-flex gap-1 rounded-2xl border border-border bg-secondary/40 p-1.5"
    >
      {LENGTHS.map((length) => {
        const active = value === length;
        return (
          <button
            key={length}
            type="button"
            role="radio"
            aria-checked={active}
            disabled={disabled}
            onClick={() => onChange(length)}
            className={cn(
              "rounded-xl px-4 py-2 text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50",
              active
                ? "bg-[image:var(--gradient-primary)] text-white shadow-[0_10px_24px_-10px_rgba(27,143,234,0.55)]"
                : "text-muted-foreground hover:bg-white/70 hover:text-foreground",
            )}
          >
            {LENGTH_LABELS[length]}
          </button>
        );
      })}
    </div>
  );
}
