import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { contentApi } from "../api/content-api";
import { mapContentError } from "../lib/error-messages";
import type { ContentDraft } from "../types/content";
import { contentKeys } from "./query-keys";

export function useDeleteContent(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (contentId: string) => contentApi.remove(contentId),
    onSuccess: (_data, contentId) => {
      queryClient.setQueryData<ContentDraft[]>(contentKeys.guest(guestId), (current) =>
        current?.filter((item) => item.id !== contentId),
      );
      toast.success("تم حذف المحتوى");
    },
    onError: (error) => {
      toast.error(mapContentError(error));
    },
  });
}
