import { AtSign, Briefcase, Camera, Globe, type LucideIcon } from "lucide-react";

import type { ContentLength, ContentPlatform, ContentSourceCategory, ContentStatus } from "../types/content";

export const PLATFORM_LABELS: Record<ContentPlatform, string> = {
  linkedin: "LinkedIn",
  x: "X",
  instagram: "Instagram",
  general: "عام",
};

// This lucide-react version ships no brand/social icons (Linkedin/Instagram/
// Twitter were removed upstream) - generic icons stand in for each
// platform's character instead.
export const PLATFORM_ICONS: Record<ContentPlatform, LucideIcon> = {
  linkedin: Briefcase,
  x: AtSign,
  instagram: Camera,
  general: Globe,
};

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

export const STATUS_LABELS: Record<ContentStatus, string> = {
  draft: "مسودة",
  approved: "معتمد",
};
