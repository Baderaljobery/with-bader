import type { ContentLimits } from "../types";
import type { SlideRole } from "../../types/design";

export const TEMPLATE_03_ID = "template-03";
export const TEMPLATE_03_NAME = "تمييز بلون موحد";
export const TEMPLATE_03_DESCRIPTION =
  "خلفية بلون أصفر خردل ساطع وموحّد، كلمة أو عبارة قصيرة جدًا عريضة، وبقية المساحة فارغة تمامًا.";

// Sampled from frontend/public/design-references/template-03/reference-01.png
export const TEMPLATE_03_COLORS = {
  background: "#F2C94D",
  text: "#151107",
};

export const TEMPLATE_03_CONTENT_LIMITS: Record<SlideRole, ContentLimits> = {
  cover: { headlineMaxChars: 24 },
  main_content: { headlineMaxChars: 24, bodyMaxChars: 90 },
  continuation: { headlineMaxChars: 24, bodyMaxChars: 90 },
  quote: { headlineMaxChars: 90 },
  quick_points: { headlineMaxChars: 20, maxPoints: 4 },
  closing: { headlineMaxChars: 20 },
};
