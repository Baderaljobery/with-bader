import { AtSign, Briefcase, Camera, Globe, type LucideIcon } from "lucide-react";

/** Shared between Content Creation and the Design Engine - both features
 * publish to the exact same four destinations and use the same draft/
 * approved lifecycle, so their label maps were identical duplicates
 * (see services/content/lib/labels.ts, services/design/lib/labels.ts). */
export type Platform = "linkedin" | "x" | "instagram" | "general";
export type DraftStatus = "draft" | "approved";

export const PLATFORM_LABELS: Record<Platform, string> = {
  linkedin: "LinkedIn",
  x: "X",
  instagram: "Instagram",
  general: "عام",
};

// This lucide-react version ships no brand/social icons (LinkedIn/
// Instagram/Twitter were removed upstream) - generic icons stand in for
// each platform's character instead.
export const PLATFORM_ICONS: Record<Platform, LucideIcon> = {
  linkedin: Briefcase,
  x: AtSign,
  instagram: Camera,
  general: Globe,
};

export const STATUS_LABELS: Record<DraftStatus, string> = {
  draft: "مسودة",
  approved: "معتمد",
};
