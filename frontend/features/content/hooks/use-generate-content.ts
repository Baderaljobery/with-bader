import { useMutation } from "@tanstack/react-query";

import { contentApi } from "../api/content-api";
import type { ContentGenerationRequest } from "../types/content";

/** No cache write and no generic onError toast here on purpose - this is a
 * preview-only call (nothing persisted), and the 409 "insufficient
 * context" case needs its own dedicated inline UI rather than a toast, so
 * the caller (generation-form.tsx) handles success/error itself. */
export function useGenerateContent(guestId: string) {
  return useMutation({
    mutationFn: (request: ContentGenerationRequest) => contentApi.generate(guestId, request),
  });
}
