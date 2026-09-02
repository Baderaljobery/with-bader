import { useQuery } from "@tanstack/react-query";

import { researchApi } from "../api/research-api";
import { researchKeys } from "./query-keys";

export function useLatestGuestResearch(guestId: string) {
  return useQuery({
    queryKey: researchKeys.latest(guestId),
    queryFn: () => researchApi.getLatest(guestId),
    enabled: Boolean(guestId),
  });
}
