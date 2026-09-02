import { useMutation, useQueryClient } from "@tanstack/react-query";

import { questionsApi } from "../api/questions-api";
import type { QuestionCreateInput, QuestionUpdateInput } from "../types/question";
import { questionKeys } from "./query-keys";

export function useCreateQuestion(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: QuestionCreateInput) => questionsApi.create(guestId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: questionKeys.guest(guestId) });
    },
  });
}

export function useUpdateQuestion(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ questionId, input }: { questionId: string; input: QuestionUpdateInput }) =>
      questionsApi.update(questionId, input),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: questionKeys.guest(guestId) });
      queryClient.invalidateQueries({ queryKey: questionKeys.detail(variables.questionId) });
    },
  });
}

export function useDeleteQuestion(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (questionId: string) => questionsApi.remove(questionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: questionKeys.guest(guestId) });
    },
  });
}
