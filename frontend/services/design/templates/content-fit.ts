import { splitPoints } from "./shared";
import type { ContentLimits } from "./types";

export type ContentFitResult = {
  fits: boolean;
  reasons: string[];
};

/** Part 13: safe typography bounds - a SOFT, fallback heuristic only.
 * Arabic text doesn't have a fixed width per character (word shape varies
 * a lot, and wrapping depends on the real container), so a raw character
 * count alone routinely both under- and over-warns. Wherever the real
 * renderer is on screen, prefer actual measured overflow instead (see
 * ../templates/use-balanced-alignment.ts's onOverflowChange, wired in by
 * multi-slide-editor.tsx and structure-preview.tsx) - this function exists
 * for the moments a live measurement isn't available yet (first paint) or
 * as planner guidance server-side, not as the source of truth once one
 * is. Never blocks saving on its own. */
export function evaluateContentFit(limits: ContentLimits, headline: string, bodyText: string): ContentFitResult {
  const reasons: string[] = [];

  if (headline.trim().length > limits.headlineMaxChars) {
    reasons.push(`العنوان أطول من المساحة المتاحة في هذا القالب (~${limits.headlineMaxChars} حرفًا)`);
  }

  if (limits.maxPoints !== undefined) {
    const points = splitPoints(bodyText, 99);
    if (points.length > limits.maxPoints) {
      reasons.push(`عدد النقاط أكثر مما يتسع له هذا القالب (الحد ${limits.maxPoints} نقاط)`);
    }
  } else if (limits.bodyMaxChars !== undefined && bodyText.trim().length > limits.bodyMaxChars) {
    reasons.push(`نص الشريحة أطول من المساحة المتاحة في هذا القالب (~${limits.bodyMaxChars} حرفًا)`);
  }

  return { fits: reasons.length === 0, reasons };
}
