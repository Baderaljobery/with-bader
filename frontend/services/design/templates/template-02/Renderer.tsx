import { forwardRef } from "react";

import { cn } from "@/lib/utils";
import { splitPoints, TemplateFrame } from "../shared";
import type { SlideRenderProps } from "../types";
import { useBalancedAlignment } from "../use-balanced-alignment";
import { TEMPLATE_02_COLORS as C } from "./config";

/** "بطاقة اسم بسيطة" - minimal paper name-card family. Reproduces the
 * reference's asymmetric corner anchoring and very large negative-space
 * ratio: most roles keep 60-75% of the frame empty, with content pinned to
 * one logical corner rather than centered or filling the frame. */
function TopStrip() {
  return <div className="absolute inset-x-0 top-0 h-[3cqh]" style={{ backgroundColor: C.topStrip }} aria-hidden="true" />;
}

export const Template02Renderer = forwardRef<HTMLDivElement, SlideRenderProps>(function Template02Renderer(
  { role, headline, bodyText, ctaText, aspectRatio, className, onOverflowChange },
  ref,
) {
  const { zoneRef, contentRef, alignment, zoneJustifyClassName, contentStyle } = useBalancedAlignment(0.5, onOverflowChange);
  // cover/main_content deliberately reproduce the reference's signature
  // bottom-right corner anchor over huge negative space (Part 41/45) -
  // that identity stays the *default*, so "center" here maps to
  // `justify-end` instead of `justify-center`. The safety fallback is the
  // same as everywhere else though: content long enough to risk crowding
  // or overflowing upward still switches to a top-anchored start.
  const cornerAnchorClassName = alignment === "center" ? "justify-end" : "justify-start";

  return (
    <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
      <TopStrip />

      {role === "quote" ? (
        <div ref={zoneRef} className={cn("flex h-full flex-col items-center p-[9cqw] text-center", zoneJustifyClassName)}>
          <div ref={contentRef} className="flex flex-col items-center gap-[3cqw]" style={contentStyle}>
            <p
              className="font-thmanyah-serif-display text-[7cqw] font-bold leading-[1.2]"
              style={{ color: C.primaryText }}
            >
              {headline}
            </p>
            {bodyText ? (
              <p className="font-thmanyah-sans text-[2.8cqw]" style={{ color: C.secondaryText }}>
                {bodyText}
              </p>
            ) : null}
          </div>
        </div>
      ) : role === "closing" ? (
        <div ref={zoneRef} className={cn("flex h-full flex-col items-center p-[9cqw] text-center", zoneJustifyClassName)}>
          <div ref={contentRef} style={contentStyle}>
            <p
              className="font-thmanyah-serif-display text-[6cqw] font-bold leading-[1.2]"
              style={{ color: C.primaryText }}
            >
              {headline}
            </p>
          </div>
        </div>
      ) : role === "continuation" ? (
        <div ref={zoneRef} className={cn("flex h-full flex-col p-[8cqw]", zoneJustifyClassName)}>
          <div ref={contentRef} style={contentStyle}>
            <div className="h-[0.3cqw] w-[14cqw]" style={{ backgroundColor: C.divider }} aria-hidden="true" />
            <p
              className="mt-[3cqw] font-thmanyah-serif-display text-[5.5cqw] font-bold leading-[1.2]"
              style={{ color: C.primaryText }}
            >
              {headline}
            </p>
            {bodyText ? (
              <p className="mt-[2.5cqw] font-thmanyah-sans text-[3cqw] leading-snug" style={{ color: C.secondaryText }}>
                {bodyText}
              </p>
            ) : null}
          </div>
        </div>
      ) : role === "quick_points" ? (
        <div ref={zoneRef} className={cn("flex h-full flex-col p-[8cqw]", zoneJustifyClassName)}>
          <div ref={contentRef} style={contentStyle}>
            <p
              className="font-thmanyah-serif-display text-[5.5cqw] font-bold leading-[1.2]"
              style={{ color: C.primaryText }}
            >
              {headline}
            </p>
            <ul className="mt-[3cqw] space-y-[2cqw]">
              {splitPoints(bodyText).map((point, index) => (
                <li key={index} className="flex items-start gap-[2cqw]">
                  <span className="font-thmanyah-sans text-[3cqw]" style={{ color: C.primaryText }}>
                    &ndash;
                  </span>
                  <span className="font-thmanyah-sans text-[3cqw] leading-snug" style={{ color: C.secondaryText }}>
                    {point}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div ref={zoneRef} className={cn("flex h-full flex-col p-[8cqw]", cornerAnchorClassName)}>
          <div ref={contentRef} style={contentStyle}>
            {bodyText && role === "cover" ? (
              <p className="mb-[1.5cqw] font-thmanyah-sans text-[2.6cqw] uppercase tracking-[0.15em]" style={{ color: C.secondaryText }}>
                {bodyText}
              </p>
            ) : null}
            <p
              className={cn(
                "font-thmanyah-serif-display font-bold leading-[1.15]",
                role === "cover" ? "text-[8cqw]" : "text-[6cqw]",
              )}
              style={{ color: C.primaryText }}
            >
              {headline}
            </p>
            {bodyText && role !== "cover" ? (
              <p className="mt-[2.5cqw] font-thmanyah-sans text-[3cqw] leading-snug" style={{ color: C.secondaryText }}>
                {bodyText}
              </p>
            ) : null}
            {ctaText ? (
              <span
                className="mt-[2.5cqw] w-fit rounded-full px-[3cqw] py-[1.2cqw] text-[2.4cqw] font-medium"
                style={{ backgroundColor: C.primaryText, color: C.topStrip }}
              >
                {ctaText}
              </span>
            ) : null}
          </div>
        </div>
      )}
    </TemplateFrame>
  );
});
