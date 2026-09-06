import { PLATFORM_ICONS, PLATFORM_LABELS, STATUS_LABELS } from "@/lib/labels";
import type { ContentLength, ContentSourceCategory } from "../types/content";

export { PLATFORM_LABELS, PLATFORM_ICONS, STATUS_LABELS };

export const LENGTH_LABELS: Record<ContentLength, string> = {
  short: "مختصر",
  medium: "متوسط",
  detailed: "تفصيلي",
};

/** Machine-readable category keys from the backend mapped to the Arabic
 * "based on" chips shown subtly on a generated/saved draft - never the raw
 * prompt or model response. */
export const SOURCE_LABELS: Record<ContentSourceCategory, string> = {
  answers: "المقابلة",
  notebook: "الدفتر",
  transcript: "نص المقابلة",
  research: "البحث",
  questions: "الأسئلة المحفوظة",
};
