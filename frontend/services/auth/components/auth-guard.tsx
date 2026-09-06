"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import type { ReactNode } from "react";

import { ApiError } from "@/lib/api/client";
import { useCurrentUser } from "../hooks/use-current-user";

/**
 * Belt-and-suspenders fallback behind proxy.ts's cookie-presence redirect:
 * proxy.ts only checks whether a session cookie exists, not whether it's
 * still valid, so a stale/expired cookie would otherwise let a private
 * page start rendering. If the real backend session check (GET
 * /api/auth/me) comes back 401, clear the cache and bounce to /login -
 * the same cache-clearing discipline as logout, since an invalid session
 * means "no session" either way.
 */
export function AuthGuard({ children }: { children: ReactNode }) {
  const { isError, error } = useCurrentUser();
  const queryClient = useQueryClient();
  const router = useRouter();

  useEffect(() => {
    if (isError && error instanceof ApiError && error.status === 401) {
      queryClient.clear();
      router.replace("/login");
    }
  }, [isError, error, queryClient, router]);

  return <>{children}</>;
}
