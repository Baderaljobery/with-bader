import { useQuery } from "@tanstack/react-query";

import { researchApi } from "../api/research-api";
import { researchKeys } from "./query-keys";

/** Fetches one research version by id. Used by the version-history panel;
 * usually served instantly from cache (seeded by useGuestResearchHistory). */
export function useGuestResearch(researchId: string | null) {
  return useQuery({
    queryKey: researchKeys.detail(researchId ?? "none"),
    queryFn: () => researchApi.getById(researchId as string),
    enabled: Boolean(researchId),
  });
}
