import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { contentApi } from "../api/content-api";
import { mapContentError } from "../lib/error-messages";
import type { ContentDraft, ContentDraftCreateInput } from "../types/content";
import { contentKeys } from "./query-keys";

/** Explicit "Save Draft" - persists a generated/edited preview for the
 * first time. Never called automatically by generation itself. */
export function useSaveContent(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: ContentDraftCreateInput) => contentApi.create(guestId, input),
    onSuccess: (draft) => {
      queryClient.setQueryData<ContentDraft[]>(contentKeys.guest(guestId), (current) =>
        current ? [draft, ...current] : [draft],
      );
      toast.success("تم حفظ المحتوى كمسودة");
    },
    onError: (error) => {
      toast.error(mapContentError(error));
    },
  });
}
