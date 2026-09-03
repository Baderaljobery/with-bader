import type { ContentLimits } from "../types";
import type { SlideRole } from "../../types/design";

export const TEMPLATE_04_ID = "template-04";
export const TEMPLATE_04_NAME = "علامة هندسية";
export const TEMPLATE_04_DESCRIPTION =
  "خلفية داكنة اللون بأشكال هندسية مجردة (ماس، مستطيلات) بتباين منخفض، وعلامة نصية هندسية كبيرة أقرب لعلامة تجارية.";

// Sampled from frontend/public/design-references/template-04/reference-01.jpg
export const TEMPLATE_04_COLORS = {
  background: "#DAD5B8",
  shape: "#C7C1A0",
  mark: "#121212",
  labelBg: "#121212",
  labelText: "#F2EFE0",
};

export const TEMPLATE_04_CONTENT_LIMITS: Record<SlideRole, ContentLimits> = {
  cover: { headlineMaxChars: 26, bodyMaxChars: 24 },
  main_content: { headlineMaxChars: 22, bodyMaxChars: 130 },
  continuation: { headlineMaxChars: 22, bodyMaxChars: 150 },
  quote: { headlineMaxChars: 110 },
  quick_points: { headlineMaxChars: 20, maxPoints: 4 },
  closing: { headlineMaxChars: 22, bodyMaxChars: 20 },
};
