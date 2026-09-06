import { useMutation, useQueryClient } from "@tanstack/react-query";

import { questionsApi } from "../api/questions-api";
import type { GeneratedQuestion } from "../types/question";
import { questionKeys } from "./query-keys";

export function useSaveGeneratedQuestions(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (questions: GeneratedQuestion[]) => questionsApi.saveGenerated(guestId, questions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: questionKeys.guest(guestId) });
    },
  });
}
