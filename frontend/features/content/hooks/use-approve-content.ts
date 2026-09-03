import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { contentApi } from "../api/content-api";
import { mapContentError } from "../lib/error-messages";
import type { ContentDraft } from "../types/content";
import { contentKeys } from "./query-keys";

/** Arabic UI label: "اعتماد المحتوى". Local status flip only - never
 * triggers Design/publishing as a side effect. */
export function useApproveContent(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contentId: string) => contentApi.approve(contentId),
    onSuccess: (draft) => {
      queryClient.setQueryData<ContentDraft[]>(contentKeys.guest(guestId), (current) =>
        current?.map((item) => (item.id === draft.id ? draft : item)),
      );
      toast.success("تم اعتماد المحتوى");
    },
    onError: (error) => {
      toast.error(mapContentError(error));
    },
  });
}
