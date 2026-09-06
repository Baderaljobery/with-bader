"use client";

import { useCurrentUser } from "@/services/auth/hooks/use-current-user";
import { Skeleton } from "@/components/ui/skeleton";

/** Subtle account footer for the sidebar (Part 48) - just the authenticated
 * user's own name/email, reusing the same current-user query Settings
 * uses. No avatar, no menu - that complexity isn't needed here. */
export function SidebarUser() {
  const { data: user, isPending } = useCurrentUser();

  if (isPending) {
    return (
      <div className="space-y-1.5 px-1">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-3 w-32" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="px-1">
      <p className="truncate text-sm font-medium text-[#161616]">{user.name}</p>
      <p className="truncate text-xs text-[#5F6368]" dir="ltr">
        {user.email}
      </p>
    </div>
  );
}
