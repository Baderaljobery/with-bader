"use client";

import { cn } from "@/lib/utils";
import { PLATFORM_ICONS, PLATFORM_LABELS } from "../lib/labels";
import type { DesignPlatform } from "../types/design";

const PLATFORMS: DesignPlatform[] = ["linkedin", "x", "instagram", "general"];

type PlatformSelectProps = {
  value: DesignPlatform;
  onChange: (platform: DesignPlatform) => void;
  disabled?: boolean;
};

export function PlatformSelect({ value, onChange, disabled }: PlatformSelectProps) {
  return (
    <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4" role="radiogroup" aria-label="لأي منصة؟">
      {PLATFORMS.map((platform) => {
        const Icon = PLATFORM_ICONS[platform];
        const active = value === platform;
        return (
          <button
            key={platform}
            type="button"
            role="radio"
            aria-checked={active}
            disabled={disabled}
            onClick={() => onChange(platform)}
            className={cn(
              "flex flex-col items-center gap-2 rounded-2xl border px-3 py-4 text-center transition-all disabled:pointer-events-none disabled:opacity-50",
              active
                ? "border-transparent bg-[image:var(--gradient-primary)] text-white shadow-[0_10px_24px_-10px_rgba(27,143,234,0.55)]"
                : "border-border bg-white text-foreground hover:border-[#1B8FEA]/40 hover:bg-secondary/40",
            )}
          >
            <Icon className="size-5" aria-hidden="true" />
            <span className="text-sm font-medium">{PLATFORM_LABELS[platform]}</span>
          </button>
        );
      })}
    </div>
  );
}
