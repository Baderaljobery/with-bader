import { AtSign, Briefcase, Camera, Globe, type LucideIcon } from "lucide-react";

import type { DesignAspectRatio, DesignPlatform, DesignStatus, SlideRole } from "../types/design";

export const PLATFORM_LABELS: Record<DesignPlatform, string> = {
  linkedin: "LinkedIn",
  x: "X",
  instagram: "Instagram",
  general: "عام",
};

// Same lucide-react limitation as Content Creation - this version ships no
// brand/social icons, so generic icons stand in for each platform.
export const PLATFORM_ICONS: Record<DesignPlatform, LucideIcon> = {
  linkedin: Briefcase,
  x: AtSign,
  instagram: Camera,
  general: Globe,
};

export const SLIDE_ROLE_LABELS: Record<SlideRole, string> = {
  cover: "افتتاحية",
  main_content: "محتوى رئيسي",
  continuation: "استكمال المحتوى",
  quote: "اقتباس",
  quick_points: "نقاط سريعة",
  closing: "خاتمة",
};

export const SLIDE_ROLE_DESCRIPTIONS: Record<SlideRole, string> = {
  cover: "أقوى عنوان، أقل نص ممكن",
  main_content: "فكرة رئيسية واحدة وشرح قصير",
  continuation: "استكمال أو دعم للفكرة السابقة",
  quote: "اقتباس أو عبارة مميزة",
  quick_points: "من 2 إلى 4 نقاط مختصرة",
  closing: "خلاصة أو خاتمة قصيرة",
};

export const SLIDE_ROLES: SlideRole[] = [
  "cover",
  "main_content",
  "continuation",
  "quote",
  "quick_points",
  "closing",
];

export const ASPECT_RATIO_LABELS: Record<DesignAspectRatio, string> = {
  "1:1": "مربع",
  "4:5": "عمودي",
  "16:9": "عريض",
  "9:16": "قصص",
};

export const STATUS_LABELS: Record<DesignStatus, string> = {
  draft: "مسودة",
  approved: "معتمد",
};
