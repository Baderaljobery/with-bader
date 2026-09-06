import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { contentApi } from "../api/content-api";
import { mapContentError } from "../lib/error-messages";
import type { ContentDraft, ContentDraftUpdateInput } from "../types/content";
import { contentKeys } from "./query-keys";

export function useUpdateContent(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ contentId, input }: { contentId: string; input: ContentDraftUpdateInput }) =>
      contentApi.update(contentId, input),
    onSuccess: (draft) => {
      queryClient.setQueryData<ContentDraft[]>(contentKeys.guest(guestId), (current) =>
        current?.map((item) => (item.id === draft.id ? draft : item)),
      );
      toast.success("تم حفظ التعديلات");
    },
    onError: (error) => {
      toast.error(mapContentError(error));
    },
  });
}
