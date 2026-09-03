import { forwardRef } from "react";

import { cn } from "@/lib/utils";
import { splitPoints, TemplateFrame } from "../shared";
import type { SlideRenderProps } from "../types";
import { TEMPLATE_04_COLORS as C } from "./config";

/** "علامة هندسية" - dark-khaki geometric wordmark/brand-mark family.
 * Reproduces the reference's layered low-contrast geometric shapes behind a
 * large bold sans wordmark, plus a small filled label bar - the one
 * template using Thmanyah Sans (not a serif), matching the reference's
 * blockier, brand-mark-like letterforms. */
function GeometricShapes({ mirrored = false }: { mirrored?: boolean }) {
  return (
    <div className={cn("pointer-events-none absolute inset-0", mirrored && "scale-x-[-1]")} aria-hidden="true">
      <span
        className="absolute top-[-8cqw] start-[-6cqw] size-[38cqw] rotate-45"
        style={{ backgroundColor: C.shape }}
      />
      <span
        className="absolute bottom-[-14cqw] end-[-10cqw] size-[46cqw] rounded-[4cqw]"
        style={{ backgroundColor: C.shape }}
      />
      <span
        className="absolute top-[8cqw] end-[10cqw] size-[6cqw] rotate-45"
        style={{ backgroundColor: C.shape }}
      />
      <span
        className="absolute bottom-[10cqw] start-[8cqw] size-[4cqw] rotate-45"
        style={{ backgroundColor: C.shape }}
      />
    </div>
  );
}

function LabelBar({ text }: { text: string }) {
  return (
    <span
      className="w-fit rounded-[1.2cqw] px-[3cqw] py-[1.4cqw] font-thmanyah-sans text-[2.6cqw] font-medium"
      style={{ backgroundColor: C.labelBg, color: C.labelText }}
    >
      {text}
    </span>
  );
}

export const Template04Renderer = forwardRef<HTMLDivElement, SlideRenderProps>(function Template04Renderer(
  { role, headline, bodyText, ctaText, aspectRatio, className },
  ref,
) {
  const label = ctaText || (role !== "main_content" && role !== "continuation" ? bodyText : "");

  return (
    <TemplateFrame ref={ref} aspectRatio={aspectRatio} background={C.background} className={className}>
      <GeometricShapes mirrored={role === "continuation"} />

      <div className="relative flex h-full flex-col p-[8cqw]">
        {role === "quote" ? (
          <div className="flex flex-1 items-center justify-center">
            <div
              className="max-w-[85%] rounded-[2cqw] px-[6cqw] py-[5cqw] text-center"
              style={{ backgroundColor: C.mark }}
            >
              <p className="font-thmanyah-sans text-[5.5cqw] font-bold leading-[1.25]" style={{ color: C.labelText }}>
                {headline}
              </p>
            </div>
          </div>
        ) : role === "quick_points" ? (
          <>
            <p className="font-thmanyah-sans text-[6cqw] font-black leading-[1.05]" style={{ color: C.mark }}>
              {headline}
            </p>
            <div className="mt-[4cqw] flex flex-1 flex-wrap content-start gap-[2cqw]">
              {splitPoints(bodyText).map((point, index) => (
                <span
                  key={index}
                  className="rounded-full px-[3.2cqw] py-[1.4cqw] font-thmanyah-sans text-[2.8cqw] font-medium"
                  style={{ backgroundColor: C.mark, color: C.labelText }}
                >
                  {point}
                </span>
              ))}
            </div>
          </>
        ) : role === "closing" ? (
          <div className="flex flex-1 flex-col items-start justify-center gap-[2.5cqw]">
            <p className="font-thmanyah-sans text-[7cqw] font-black leading-[1.05]" style={{ color: C.mark }}>
              {headline}
            </p>
            {label ? <LabelBar text={label} /> : null}
          </div>
        ) : (
          <>
            <p
              className={cn(
                "font-thmanyah-sans font-black leading-[1.05]",
                role === "cover" ? "text-[9cqw]" : "text-[6.5cqw]",
              )}
              style={{ color: C.mark }}
            >
              {headline}
            </p>
            {bodyText && (role === "main_content" || role === "continuation") ? (
              <p className="mt-[3cqw] max-w-[80%] font-thmanyah-sans text-[3.2cqw] leading-snug" style={{ color: C.mark, opacity: 0.85 }}>
                {bodyText}
              </p>
            ) : null}
            {label ? (
              <div className="mt-auto">
                <LabelBar text={label} />
              </div>
            ) : null}
          </>
        )}
      </div>
    </TemplateFrame>
  );
});
