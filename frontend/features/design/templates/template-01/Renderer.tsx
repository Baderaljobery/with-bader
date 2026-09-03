import { forwardRef } from "react";

import { cn } from "@/lib/utils";
import { splitPoints, TemplateFrame } from "../shared";
import type { SlideRenderProps } from "../types";
import { TEMPLATE_01_COLORS as C } from "./config";

/** "ملصق سينمائي جريء" - bold cinematic-poster family. Reproduces the
 * reference's warm terracotta ground, oversized cream serif headline, dark
 * subtitle line directly under it, and a dramatic dark band anchoring the
 * bottom of the frame - rebuilt as an abstract two-shape "figures" motif
 * instead of the reference's actual photographs (Part 42: never reproduce
 * third-party photos/copy, only the composition/mood). */
function DotRow() {
  return (
    <div className="flex items-center gap-[1.2cqw]" aria-hidden="true">
      {[0, 1, 2, 3].map((i) => (
        <span key={i} className="size-[1.6cqw] rounded-full" style={{ backgroundColor: C.accent }} />
      ))}
    </div>
  );
}

function FigureBand({ tall = true }: { tall?: boolean }) {
  return (
    <div
      className={cn("relative w-full overflow-hidden rounded-t-[3cqw]", tall ? "h-[34cqh]" : "h-[22cqh]")}
      style={{ backgroundImage: `linear-gradient(160deg, ${C.bottomBandFrom}, ${C.bottomBandTo})` }}
      aria-hidden="true"
    >
      <span
        className="absolute -bottom-[10cqw] start-[6cqw] size-[34cqw] rounded-full opacity-90"
        style={{ backgroundColor: "#00000030" }}
      />
      <span
        className="absolute -bottom-[14cqw] end-[2cqw] size-[40cqw] rounded-full opacity-70"
        style={{ backgroundColor: "#00000022" }}
      />
    </div>
  );
}

export const Template01Renderer = forwardRef<HTMLDivElement, SlideRenderProps>(function Template01Renderer(
  { role, headline, bodyText, ctaText, aspectRatio, className },
  ref,
) {
  return (
    <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
      <div className="flex h-full flex-col p-[7cqw]">
        {role === "quote" ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-[3cqw] text-center">
            <span
              className="font-thmanyah-serif-display text-[14cqw] leading-none"
              style={{ color: C.accent }}
              aria-hidden="true"
            >
              &rdquo;
            </span>
            <p className="font-thmanyah-serif-display text-[7cqw] font-bold leading-[1.15]" style={{ color: C.headline }}>
              {headline}
            </p>
            {bodyText ? (
              <p className="font-thmanyah-sans text-[3.2cqw] leading-snug" style={{ color: C.headline }}>
                {bodyText}
              </p>
            ) : null}
          </div>
        ) : role === "closing" ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-[2cqw] text-center">
            <p className="font-thmanyah-serif-display text-[8cqw] font-bold leading-[1.1]" style={{ color: C.headline }}>
              {headline}
            </p>
            {bodyText ? (
              <p className="font-thmanyah-sans text-[3cqw] leading-snug" style={{ color: C.headline }}>
                {bodyText}
              </p>
            ) : null}
          </div>
        ) : role === "quick_points" ? (
          <>
            <p className="font-thmanyah-serif-display text-[7cqw] font-bold leading-[1.15]" style={{ color: C.headline }}>
              {headline}
            </p>
            <ul className="mt-[4cqw] flex-1 space-y-[3cqw]">
              {splitPoints(bodyText).map((point, index) => (
                <li key={index} className="flex items-start gap-[2.5cqw]">
                  <span
                    className="font-thmanyah-serif-display text-[5cqw] font-bold leading-none"
                    style={{ color: C.accent }}
                  >
                    {index + 1}
                  </span>
                  <span className="font-thmanyah-sans text-[3.4cqw] leading-snug" style={{ color: C.subtitle }}>
                    {point}
                  </span>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <>
            <p
              className={cn(
                "font-thmanyah-serif-display font-bold leading-[1.08]",
                role === "cover" ? "text-[9cqw]" : "text-[6.5cqw]",
              )}
              style={{ color: C.headline }}
            >
              {headline}
            </p>
            {bodyText ? (
              <p
                className={cn(
                  "font-thmanyah-sans leading-snug",
                  role === "cover" ? "mt-[2.4cqw] text-[3.2cqw]" : "mt-[3cqw] text-[3.6cqw]",
                )}
                style={{ color: C.subtitle }}
              >
                {bodyText}
              </p>
            ) : null}

            {ctaText ? (
              <span
                className="mt-[2.5cqw] inline-block w-fit rounded-full px-[3cqw] py-[1.2cqw] text-[2.6cqw] font-medium"
                style={{ backgroundColor: C.subtitle, color: C.headline }}
              >
                {ctaText}
              </span>
            ) : null}

            {role === "cover" || role === "main_content" ? (
              <div className="-mx-[7cqw] mt-auto flex flex-col gap-[2cqw] px-[7cqw] pt-[3cqw]">
                <DotRow />
                <FigureBand tall={role === "cover"} />
              </div>
            ) : null}
          </>
        )}
      </div>
    </TemplateFrame>
  );
});
