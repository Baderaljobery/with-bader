import { forwardRef } from "react";

import { cn } from "@/lib/utils";
import { splitPoints, TemplateFrame } from "../shared";
import type { SlideRenderProps } from "../types";
import { TEMPLATE_02_COLORS as C } from "./config";

/** "بطاقة اسم بسيطة" - minimal paper name-card family. Reproduces the
 * reference's asymmetric corner anchoring and very large negative-space
 * ratio: most roles keep 60-75% of the frame empty, with content pinned to
 * one logical corner rather than centered or filling the frame. */
function TopStrip() {
  return <div className="absolute inset-x-0 top-0 h-[3cqh]" style={{ backgroundColor: C.topStrip }} aria-hidden="true" />;
}

export const Template02Renderer = forwardRef<HTMLDivElement, SlideRenderProps>(function Template02Renderer(
  { role, headline, bodyText, ctaText, aspectRatio, className },
  ref,
) {
  return (
    <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
      <TopStrip />

      {role === "quote" ? (
        <div className="flex h-full flex-col items-center justify-center gap-[3cqw] p-[9cqw] text-center">
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
      ) : role === "closing" ? (
        <div className="flex h-full flex-col items-center justify-center p-[9cqw] text-center">
          <p
            className="font-thmanyah-serif-display text-[6cqw] font-bold leading-[1.2]"
            style={{ color: C.primaryText }}
          >
            {headline}
          </p>
        </div>
      ) : role === "continuation" ? (
        <div className="flex h-full flex-col justify-start p-[8cqw] pt-[10cqw]">
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
      ) : role === "quick_points" ? (
        <div className="flex h-full flex-col justify-end p-[8cqw]">
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
      ) : (
        <div className="flex h-full flex-col justify-end p-[8cqw]">
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
      )}
    </TemplateFrame>
  );
});
