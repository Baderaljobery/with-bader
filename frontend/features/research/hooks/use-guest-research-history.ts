import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

import { researchApi } from "../api/research-api";
import { researchKeys } from "./query-keys";

/**
 * Lazy (caller controls `enabled`) - the backend has no lightweight
 * "metadata only" history endpoint, so this pulls the full payload for
 * every version. To avoid a redundant re-fetch when a specific version is
 * then opened, each item is seeded into the `researchKeys.detail(id)` cache
 * that useGuestResearch() reads from.
 */
export function useGuestResearchHistory(guestId: string, options?: { enabled?: boolean }) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: researchKeys.history(guestId),
    queryFn: () => researchApi.getHistory(guestId),
    enabled: (options?.enabled ?? true) && Boolean(guestId),
  });

  useEffect(() => {
    if (!query.data) return;
    for (const item of query.data) {
      queryClient.setQueryData(researchKeys.detail(item.id), item);
    }
  }, [query.data, queryClient]);

  return query;
}
