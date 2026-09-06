import { useMutation } from "@tanstack/react-query";

import { questionsApi } from "../api/questions-api";
import type { QuestionGenerationRequest } from "../types/question";

/** Preview only - the backend never persists anything from this call. */
export function useGenerateQuestions(guestId: string) {
  return useMutation({
    mutationFn: (request: QuestionGenerationRequest) => questionsApi.generate(guestId, request),
  });
}
