import { useMutation } from "@tanstack/react-query";

import { designApi } from "../api/design-api";
import type { DesignPlanRequest } from "../types/design";

/** No cache write and no generic onError toast on purpose - nothing is
 * persisted here (see api/design.py's plan endpoint), and the 409
 * "insufficient context" case needs its own dedicated inline UI rather
 * than a toast, so the caller (configuration-form.tsx) handles it. */
export function usePlanDesign(guestId: string) {
  return useMutation({
    mutationFn: (request: DesignPlanRequest) => designApi.plan(guestId, request),
  });
}
