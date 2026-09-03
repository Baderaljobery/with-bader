"use client";

import { forwardRef } from "react";

import { cn } from "@/lib/utils";
import type { DesignAspectRatio } from "../types/design";

export const ASPECT_RATIO_CLASS: Record<DesignAspectRatio, string> = {
  "1:1": "aspect-square",
  "4:5": "aspect-[4/5]",
  "16:9": "aspect-video",
  "9:16": "aspect-[9/16]",
};

/** Export/full-resolution pixel size per ratio (Part 33) - 1080px on the
 * shorter/base edge, matching common social-ready dimensions. */
export const ASPECT_RATIO_PX: Record<DesignAspectRatio, { width: number; height: number }> = {
  "1:1": { width: 1080, height: 1080 },
  "4:5": { width: 1080, height: 1350 },
  "16:9": { width: 1920, height: 1080 },
  "9:16": { width: 1080, height: 1920 },
};

type TemplateFrameProps = {
  aspectRatio: DesignAspectRatio;
  background: string;
  className?: string;
  children: React.ReactNode;
};

/** Shared outer shell every template renders into - a fixed-color,
 * fixed-radius aspect-ratio box that is also a CSS container (`@container`).
 * Every template's internal type scale uses container-query units (cqw/cqh)
 * instead of px/vw, so the exact same markup produces an identical,
 * proportionally-scaled result whether it's a 96px thumbnail, the live
 * editor preview, or a 1080px+ PNG export (Part 6: deterministic, no
 * separate "compact" prop/branch needed). */
export const TemplateFrame = forwardRef<HTMLDivElement, TemplateFrameProps>(function TemplateFrame(
  { aspectRatio, background, className, children },
  ref,
) {
  return (
    <div
      ref={ref}
      className={cn(
        "relative w-full overflow-hidden rounded-2xl @container",
        ASPECT_RATIO_CLASS[aspectRatio],
        className,
      )}
      style={{ backgroundColor: background }}
    >
      {children}
    </div>
  );
});

/** quick_points slides carry their points as newline-separated lines inside
 * body_text (see backend/app/design_planning/prompts.py rule for that
 * role) - this is the one place that convention is parsed back out. */
export function splitPoints(bodyText: string, max = 4): string[] {
  return bodyText
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(0, max);
}
