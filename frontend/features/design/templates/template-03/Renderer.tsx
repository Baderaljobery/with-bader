import { forwardRef } from "react";

import { splitPoints, TemplateFrame } from "../shared";
import type { SlideRenderProps } from "../types";
import { TEMPLATE_03_COLORS as C } from "./config";

/** "تمييز بلون موحد" - single flat-color word-emphasis family. The
 * reference is essentially one bold word on one solid color with almost
 * everything else left empty - every role variant here keeps that
 * extreme minimalism, only moving where the (still very short) text sits
 * and how much of it there is. */
export const Template03Renderer = forwardRef<HTMLDivElement, SlideRenderProps>(function Template03Renderer(
  { role, headline, bodyText, aspectRatio, className },
  ref,
) {
  if (role === "quote") {
    return (
      <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
        <div className="flex h-full flex-col items-center justify-center gap-[2cqw] p-[10cqw] text-center">
          <span className="font-thmanyah-serif-display text-[10cqw] leading-none" style={{ color: C.text }} aria-hidden="true">
            &rdquo;
          </span>
          <p className="font-thmanyah-serif-display text-[7cqw] font-bold leading-[1.15]" style={{ color: C.text }}>
            {headline}
          </p>
        </div>
      </TemplateFrame>
    );
  }

  if (role === "closing") {
    return (
      <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
        <div className="flex h-full items-center justify-center p-[10cqw] text-center">
          <p className="font-thmanyah-serif-display text-[6.5cqw] font-bold leading-[1.15]" style={{ color: C.text }}>
            {headline}
          </p>
        </div>
      </TemplateFrame>
    );
  }

  if (role === "quick_points") {
    return (
      <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
        <div className="flex h-full flex-col justify-center gap-[4cqw] p-[10cqw]">
          {splitPoints(bodyText).map((point, index) => (
            <p key={index} className="font-thmanyah-serif-display text-[6cqw] font-bold leading-[1.1]" style={{ color: C.text }}>
              {point}
            </p>
          ))}
        </div>
      </TemplateFrame>
    );
  }

  const headlineAtTop = role === "cover" || role === "main_content";

  return (
    <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
      <div className="flex h-full flex-col p-[9cqw]">
        {headlineAtTop ? (
          <p
            className="font-thmanyah-serif-display font-bold leading-[1.05] text-[10cqw]"
            style={{ color: C.text }}
          >
            {headline}
          </p>
        ) : null}

        {bodyText ? (
          <p
            className={`font-thmanyah-sans text-[2.6cqw] leading-snug ${headlineAtTop ? "mt-auto" : "mt-0"}`}
            style={{ color: C.text, opacity: 0.75 }}
          >
            {bodyText}
          </p>
        ) : null}

        {!headlineAtTop ? (
          <p
            className="mt-auto font-thmanyah-serif-display font-bold leading-[1.05] text-[10cqw]"
            style={{ color: C.text }}
          >
            {headline}
          </p>
        ) : null}
      </div>
    </TemplateFrame>
  );
});
