import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { designApi } from "../api/design-api";
import { mapDesignError } from "../lib/error-messages";
import type { DesignDraft, DesignSlideUpdateInput } from "../types/design";
import { designKeys } from "./query-keys";

export function useUpdateSlide(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      designId,
      slideIndex,
      input,
    }: {
      designId: string;
      slideIndex: number;
      input: DesignSlideUpdateInput;
    }) => designApi.updateSlide(designId, slideIndex, input),
    onSuccess: (slide) => {
      queryClient.setQueryData<DesignDraft[]>(designKeys.guest(guestId), (current) =>
        current?.map((draft) =>
          draft.id === slide.design_draft_id
            ? { ...draft, slides: draft.slides.map((s) => (s.slide_index === slide.slide_index ? slide : s)) }
            : draft,
        ),
      );
      toast.success("تم حفظ التعديلات");
    },
    onError: (error) => {
      toast.error(mapDesignError(error));
    },
  });
}
