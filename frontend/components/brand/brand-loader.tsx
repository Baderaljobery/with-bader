"use client";

import { useEffect, useState } from "react";

import { AnimatedLogo } from "@/components/brand/animated-logo";
import { BackgroundPattern } from "@/components/brand/background-pattern";
import { cn } from "@/lib/utils";

const EXIT_MS = 140;

export type BrandLoaderProps = {
  /** The REAL loading condition (a query's isPending/isFetching, a
   * mutation's isPending, a route Suspense boundary, etc). BrandLoader
   * never invents its own timing - it shows for exactly as long as this
   * is true, plus a short fade so it doesn't leave a visual hard cut. */
  loading: boolean;
  /** "fullscreen": covers the viewport and blocks interaction - only for
   * moments the app genuinely cannot continue. "section": fills its
   * parent, for a page/content area while the surrounding chrome (e.g.
   * the sidebar) stays usable. */
  variant?: "fullscreen" | "section";
  className?: string;
  label?: string;
};

/**
 * Loading indicator built on the animated With Bader logo. Duration is
 * owned entirely by the caller's `loading` boolean, never by the logo
 * animation itself: AnimatedLogo loops for as long as BrandLoader stays
 * mounted, and unmounts the instant `loading` goes false (after a brief
 * fade, never a wait for the loop to reach any particular point).
 */
export function BrandLoader({ loading, variant = "section", className, label }: BrandLoaderProps) {
  // `exiting` only ever flips true via the timers below, both scheduled in
  // a callback rather than synchronously in the effect body - visibility
  // itself (`loading || exiting`) is derived at render time, not mirrored
  // into state, so there's no separate "turn on" state to manage.
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    if (loading) return;
    const raf = requestAnimationFrame(() => setExiting(true));
    const timer = setTimeout(() => setExiting(false), EXIT_MS);
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(timer);
    };
  }, [loading]);

  const visible = loading || exiting;
  if (!visible) return null;

  const fadingOut = !loading;

  return (
    <div
      role="status"
      aria-live="polite"
      aria-label={label ?? "جارٍ التحميل"}
      className={cn(
        "flex items-center justify-center transition-opacity ease-out",
        variant === "fullscreen" ? "fixed inset-0 z-[9999]" : "min-h-40 w-full py-12",
        className,
      )}
      style={{
        opacity: fadingOut ? 0 : 1,
        transitionDuration: `${EXIT_MS}ms`,
        ...(variant === "fullscreen"
          ? { backgroundColor: "#f5f8fb", pointerEvents: fadingOut ? "none" : "auto" }
          : undefined),
      }}
    >
      {variant === "fullscreen" && <BackgroundPattern />}
      <div
        className={cn("relative", variant === "fullscreen" ? "w-[180px]" : "w-[120px]")}
        style={{ aspectRatio: "970 / 460" }}
      >
        <AnimatedLogo />
      </div>
    </div>
  );
}
