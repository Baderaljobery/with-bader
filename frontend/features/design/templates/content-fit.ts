import { splitPoints } from "./shared";
import type { ContentLimits } from "./types";

export type ContentFitResult = {
  fits: boolean;
  reasons: string[];
};

/** Part 13: safe typography bounds. Templates render text at a fixed
 * container-scaled size per role (never a "shrink until it fits"
 * mechanism, which risks unreadably tiny text) - so instead of resizing,
 * content that exceeds a role/template's realistic budget surfaces a
 * warning here, both in the structure-preview step and the live editor,
 * so the user can shorten it themselves before it ships looking cramped. */
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
