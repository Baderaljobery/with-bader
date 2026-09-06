import { useMutation, useQueryClient } from "@tanstack/react-query";

import { questionsApi } from "../api/questions-api";
import { questionKeys } from "./query-keys";

export function useAcceptImprovement(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ questionId, improvedText }: { questionId: string; improvedText: string }) =>
      questionsApi.acceptImprovement(questionId, improvedText),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: questionKeys.guest(guestId) });
      queryClient.invalidateQueries({ queryKey: questionKeys.detail(variables.questionId) });
      queryClient.invalidateQueries({ queryKey: questionKeys.versions(variables.questionId) });
    },
  });
}
