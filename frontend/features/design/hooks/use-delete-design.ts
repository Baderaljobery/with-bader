import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { designApi } from "../api/design-api";
import { mapDesignError } from "../lib/error-messages";
import type { DesignDraft } from "../types/design";
import { designKeys } from "./query-keys";

export function useDeleteDesign(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (designId: string) => designApi.remove(designId),
    onSuccess: (_data, designId) => {
      queryClient.setQueryData<DesignDraft[]>(designKeys.guest(guestId), (current) =>
        current?.filter((item) => item.id !== designId),
      );
      toast.success("تم حذف التصميم");
    },
    onError: (error) => {
      toast.error(mapDesignError(error));
    },
  });
}
