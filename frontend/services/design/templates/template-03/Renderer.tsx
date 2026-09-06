import { forwardRef } from "react";

import { cn } from "@/lib/utils";
import { splitPoints, TemplateFrame } from "../shared";
import type { SlideRenderProps } from "../types";
import { useBalancedAlignment } from "../use-balanced-alignment";
import { TEMPLATE_03_COLORS as C } from "./config";

/** "تمييز بلون موحد" - single flat-color word-emphasis family. The
 * reference is essentially one bold word on one solid color with almost
 * everything else left empty - every role variant here keeps that
 * extreme minimalism, only moving where the (still very short) text sits
 * and how much of it there is. */
export const Template03Renderer = forwardRef<HTMLDivElement, SlideRenderProps>(function Template03Renderer(
  { role, headline, bodyText, aspectRatio, className, onOverflowChange },
  ref,
) {
  const { zoneRef, contentRef, zoneJustifyClassName, contentStyle } = useBalancedAlignment(0.5, onOverflowChange);

  if (role === "quote") {
    return (
      <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
        <div ref={zoneRef} className={cn("flex h-full flex-col items-center p-[10cqw] text-center", zoneJustifyClassName)}>
          <div ref={contentRef} className="flex flex-col items-center gap-[2cqw]" style={contentStyle}>
            <span className="font-thmanyah-serif-display text-[10cqw] leading-none" style={{ color: C.text }} aria-hidden="true">
              &rdquo;
            </span>
            <p className="font-thmanyah-serif-display text-[7cqw] font-bold leading-[1.15]" style={{ color: C.text }}>
              {headline}
            </p>
          </div>
        </div>
      </TemplateFrame>
    );
  }

  if (role === "closing") {
    return (
      <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
        <div ref={zoneRef} className={cn("flex h-full flex-col items-center p-[10cqw] text-center", zoneJustifyClassName)}>
          <div ref={contentRef} style={contentStyle}>
            <p className="font-thmanyah-serif-display text-[6.5cqw] font-bold leading-[1.15]" style={{ color: C.text }}>
              {headline}
            </p>
          </div>
        </div>
      </TemplateFrame>
    );
  }

  if (role === "quick_points") {
    return (
      <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
        <div ref={zoneRef} className={cn("flex h-full flex-col p-[10cqw]", zoneJustifyClassName)}>
          <div ref={contentRef} className="flex flex-col gap-[4cqw]" style={contentStyle}>
            {splitPoints(bodyText).map((point, index) => (
              <p key={index} className="font-thmanyah-serif-display text-[6cqw] font-bold leading-[1.1]" style={{ color: C.text }}>
                {point}
              </p>
            ))}
          </div>
        </div>
      </TemplateFrame>
    );
  }

  return (
    <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
      <div ref={zoneRef} className={cn("flex h-full flex-col p-[9cqw]", zoneJustifyClassName)}>
        <div ref={contentRef} style={contentStyle}>
          <p className="font-thmanyah-serif-display font-bold leading-[1.05] text-[10cqw]" style={{ color: C.text }}>
            {headline}
          </p>
          {bodyText ? (
            <p className="mt-[2.5cqw] font-thmanyah-sans text-[2.6cqw] leading-snug" style={{ color: C.text, opacity: 0.75 }}>
              {bodyText}
            </p>
          ) : null}
        </div>
      </div>
    </TemplateFrame>
  );
});
