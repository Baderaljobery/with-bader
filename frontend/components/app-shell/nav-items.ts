import { BarChart3, CalendarDays, FileSearch, Home, Settings } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type NavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
};

export const mainNavItems: NavItem[] = [
  { href: "/", label: "الرئيسية", icon: Home },
  { href: "/text-extract", label: "استخراج النصوص", icon: FileSearch },
  { href: "/calendar", label: "التقويم", icon: CalendarDays },
  { href: "/statistics", label: "الإحصائيات", icon: BarChart3 },
  { href: "/settings", label: "الإعدادات", icon: Settings },
];
