import { useMutation } from "@tanstack/react-query";

import { questionsApi } from "../api/questions-api";
import type { QuestionImprovementRequest } from "../types/question";

/** Preview only - never modifies the question or creates a version. */
export function useImproveQuestion() {
  return useMutation({
    mutationFn: ({
      questionId,
      request,
    }: {
      questionId: string;
      request?: QuestionImprovementRequest;
    }) => questionsApi.improve(questionId, request),
  });
}
