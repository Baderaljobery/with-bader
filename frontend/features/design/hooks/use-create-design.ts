import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { designApi } from "../api/design-api";
import { mapDesignError } from "../lib/error-messages";
import type { DesignCreateRequest, DesignDraft } from "../types/design";
import { designKeys } from "./query-keys";

/** Persists the user-approved slide structure (still no images - see
 * useGenerateDesignImages, which the caller chains into immediately after
 * this succeeds). */
export function useCreateDesign(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: DesignCreateRequest) => designApi.create(guestId, request),
    onSuccess: (draft) => {
      queryClient.setQueryData<DesignDraft[]>(designKeys.guest(guestId), (current) =>
        current ? [draft, ...current] : [draft],
      );
    },
    onError: (error) => {
      toast.error(mapDesignError(error));
    },
  });
}
