import type { ContentLimits } from "../types";
import type { SlideRole } from "../../types/design";

export const TEMPLATE_01_ID = "template-01";
export const TEMPLATE_01_NAME = "ملصق سينمائي جريء";
export const TEMPLATE_01_DESCRIPTION =
  "خلفية تراكوتا دافئة، عنوان ضخم بخط Thmanyah Serif Display، شريط سفلي درامي بطابع بوستر سينمائي.";

// Sampled from frontend/public/design-references/template-01/reference-01.png
export const TEMPLATE_01_COLORS = {
  background: "#C1472C",
  headline: "#F4E8D4",
  subtitle: "#241812",
  accent: "#F4E8D4",
  bottomBandFrom: "#3A1D14",
  bottomBandTo: "#1B0F0A",
};

export const TEMPLATE_01_CONTENT_LIMITS: Record<SlideRole, ContentLimits> = {
  cover: { headlineMaxChars: 60, bodyMaxChars: 70 },
  main_content: { headlineMaxChars: 50, bodyMaxChars: 160 },
  continuation: { headlineMaxChars: 40, bodyMaxChars: 180 },
  quote: { headlineMaxChars: 140 },
  quick_points: { headlineMaxChars: 40, maxPoints: 4 },
  closing: { headlineMaxChars: 60, bodyMaxChars: 60 },
};
