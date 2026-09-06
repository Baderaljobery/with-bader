import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { authApi } from "../api/auth-api";

/** Real backend logout (clears the HttpOnly session cookie server-side) -
 * never just a client-side redirect. Also clears the ENTIRE TanStack Query
 * cache (not just the current-user entry) so a different user logging in
 * on the same browser afterwards can never briefly see this user's cached
 * guests/calendar/statistics/content/designs. */
export function useLogout() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      queryClient.clear();
      router.push("/login");
    },
  });
}
