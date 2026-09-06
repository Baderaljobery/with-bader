"use client";

import { useLayoutEffect, useRef, useState } from "react";

import { getVerticalAlignment, type VerticalAlignment } from "./vertical-alignment";

/** Applied as the text block's padding-top only when top-aligned (Part 3:
 * top alignment is a fallback, and even then the text should never sit
 * flush against the very top edge of its safe area). Expressed in the
 * same container-query unit every template already uses, so it scales
 * identically at thumbnail/editor/export sizes. */
const TOP_OFFSET = "2.5cqw";

type BalancedAlignment = {
  /** Attach to the flexible safe-content container - the box whose
   * rendered height defines "available space" (typically `flex-1` within
   * its parent column, sized by whatever fixed/decorative siblings -
   * figure bands, label pills, pagination dots, CTA pills, image areas -
   * already take up). */
  zoneRef: React.RefObject<HTMLDivElement | null>;
  /** Attach to the inner wrapper holding just the text itself (headline/
   * body/points/etc) - its natural, unstretched height is what gets
   * measured and compared against the zone's available height. */
  contentRef: React.RefObject<HTMLDivElement | null>;
  alignment: VerticalAlignment;
  /** `justify-center` or `justify-start` - apply to the zone element. */
  zoneJustifyClassName: string;
  /** Spread onto the content wrapper's `style` - adds the fixed top
   * offset only when top-aligned, `undefined` (no-op) when centered. */
  contentStyle: React.CSSProperties | undefined;
};

/**
 * Measures a rendered text block against its safe content area and picks
 * between vertically centering it (default) or top-aligning it with a
 * fixed offset (fallback for content tall enough that centering would
 * crowd the composition) - see `getVerticalAlignment`.
 *
 * Render-based and reactive: a `ResizeObserver` re-measures whenever the
 * text (and therefore its rendered height) changes, so editing a slide's
 * copy live updates the alignment with no manual per-slide tuning.
 *
 * The same measurement also answers a second, stricter question: does the
 * content genuinely not fit at all (taller/wider than its safe area even
 * once top-aligned)? `onOverflowChange`, when given, is called with that
 * real answer on every re-measure - this is the "measure the actual
 * rendered container" overflow check the editor's save-time warning
 * should trust over a raw character count (see ../content-fit.ts).
 */
export function useBalancedAlignment(
  thresholdRatio = 0.5,
  onOverflowChange?: (overflows: boolean) => void,
): BalancedAlignment {
  const zoneRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [alignment, setAlignment] = useState<VerticalAlignment>("center");
  // Ref, not a direct dependency - a caller passing a fresh inline
  // function every render (rather than a stable useState setter) must
  // never cause the ResizeObserver below to be torn down and recreated.
  // Synced in its own effect (never written during render - React refs
  // must not be mutated in the render body).
  const onOverflowChangeRef = useRef(onOverflowChange);
  useLayoutEffect(() => {
    onOverflowChangeRef.current = onOverflowChange;
  });

  useLayoutEffect(() => {
    const zone = zoneRef.current;
    const content = contentRef.current;
    if (!zone || !content) return;

    const measure = () => {
      setAlignment(getVerticalAlignment(content.scrollHeight, zone.clientHeight, thresholdRatio));
      onOverflowChangeRef.current?.(
        content.scrollHeight > zone.clientHeight || content.scrollWidth > zone.clientWidth,
      );
    };
    measure();

    const observer = new ResizeObserver(measure);
    observer.observe(zone);
    observer.observe(content);
    return () => observer.disconnect();
  }, [thresholdRatio]);

  return {
    zoneRef,
    contentRef,
    alignment,
    zoneJustifyClassName: alignment === "center" ? "justify-center" : "justify-start",
    contentStyle: alignment === "top" ? { paddingTop: TOP_OFFSET } : undefined,
  };
}
