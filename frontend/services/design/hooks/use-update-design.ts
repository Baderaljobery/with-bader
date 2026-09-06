import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { designApi } from "../api/design-api";
import { mapDesignError } from "../lib/error-messages";
import type { DesignDraft, DesignDraftUpdateInput } from "../types/design";
import { designKeys } from "./query-keys";

export function useUpdateDesign(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ designId, input }: { designId: string; input: DesignDraftUpdateInput }) =>
      designApi.update(designId, input),
    onSuccess: (draft) => {
      queryClient.setQueryData<DesignDraft[]>(designKeys.guest(guestId), (current) =>
        current?.map((item) => (item.id === draft.id ? draft : item)),
      );
      toast.success("تم حفظ التعديلات");
    },
    onError: (error) => {
      toast.error(mapDesignError(error));
    },
  });
}
