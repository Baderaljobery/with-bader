import { useMutation, useQueryClient } from "@tanstack/react-query";

import { questionKeys } from "@/services/questions/hooks/query-keys";
import { interviewApi } from "../api/interview-api";
import type { QuestionAnswerUpdateInput } from "../types/interview";

export function useUpdateQuestionAnswer(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      questionId,
      input,
    }: {
      questionId: string;
      input: QuestionAnswerUpdateInput;
    }) => interviewApi.updateQuestionAnswer(questionId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: questionKeys.guest(guestId) });
    },
  });
}
