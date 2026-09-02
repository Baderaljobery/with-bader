import Image from "next/image";

import { cn } from "@/lib/utils";

// Natural pixel dimensions of the source assets (public/logo-full.png,
// public/logo-icon.png) - cropped from the uploaded brand reference (a
// genuine transparent PNG export). Kept here so next/image can size
// correctly without re-measuring the files.
const FULL_RATIO = { width: 1688, height: 681 };
const ICON_RATIO = { width: 677, height: 681 };

const HEIGHTS = {
  sm: "h-6",
  md: "h-8",
  nav: "h-10",
  lg: "h-12",
} as const;

type LogoProps = {
  size?: keyof typeof HEIGHTS;
  iconOnly?: boolean;
  className?: string;
};

export function Logo({ size = "md", iconOnly = false, className }: LogoProps) {
  const dimensions = iconOnly ? ICON_RATIO : FULL_RATIO;

  return (
    <Image
      src={iconOnly ? "/logo-icon.png" : "/logo-full.png"}
      alt="With Bader"
      width={dimensions.width}
      height={dimensions.height}
      priority
      className={cn(HEIGHTS[size], "w-auto", className)}
    />
  );
}
