import { useMutation, useQueryClient } from "@tanstack/react-query";

import { questionsApi } from "../api/questions-api";
import type { QuestionGenerationSaveRequest } from "../types/question";
import { questionKeys } from "./query-keys";

export function useSaveGeneratedQuestions(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: QuestionGenerationSaveRequest) =>
      questionsApi.saveGenerated(guestId, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: questionKeys.guest(guestId) });
    },
  });
}
