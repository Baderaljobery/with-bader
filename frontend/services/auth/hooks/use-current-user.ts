import { useQuery } from "@tanstack/react-query";

import { authApi } from "../api/auth-api";
import { authKeys } from "./query-keys";

/** The single source of truth for "who is logged in" - Settings, the
 * sidebar, and the protected-route guard all read this same query instead
 * of duplicating a current-user fetch. A 401 here means "not logged in",
 * not a transient failure, so it never retries. */
export function useCurrentUser() {
  return useQuery({
    queryKey: authKeys.currentUser,
    queryFn: authApi.getCurrentUser,
    retry: false,
  });
}
