import type { ContentLimits } from "../types";
import type { SlideRole } from "../../types/design";

export const TEMPLATE_02_ID = "template-02";
export const TEMPLATE_02_NAME = "بطاقة اسم بسيطة";
export const TEMPLATE_02_DESCRIPTION =
  "خلفية ورقية هادئة بلون أخضر مريح، نص عريض في زاوية الإطار، ومساحة فارغة واسعة جدًا - تصميم أدنى حدًا.";

// Sampled from frontend/public/design-references/template-02/reference-01.jpg
export const TEMPLATE_02_COLORS = {
  background: "#8FAD84",
  topStrip: "#F1EEE1",
  primaryText: "#16210F",
  secondaryText: "#33402A",
  divider: "#00000022",
};

export const TEMPLATE_02_CONTENT_LIMITS: Record<SlideRole, ContentLimits> = {
  cover: { headlineMaxChars: 44, bodyMaxChars: 40 },
  main_content: { headlineMaxChars: 36, bodyMaxChars: 130 },
  continuation: { headlineMaxChars: 30, bodyMaxChars: 150 },
  quote: { headlineMaxChars: 120 },
  quick_points: { headlineMaxChars: 30, maxPoints: 4 },
  closing: { headlineMaxChars: 40, bodyMaxChars: 40 },
};
