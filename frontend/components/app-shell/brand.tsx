import type { ComponentProps } from "react";

import { Logo } from "@/components/brand/logo";

type BrandProps = {
  size?: ComponentProps<typeof Logo>["size"];
  className?: string;
};

export function Brand({ size = "md", className = "px-1" }: BrandProps) {
  return (
    <div className={className}>
      <Logo size={size} />
    </div>
  );
}
