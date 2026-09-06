import { useMutation, useQueryClient } from "@tanstack/react-query";

import { questionKeys } from "@/services/questions/hooks/query-keys";
import { interviewApi } from "../api/interview-api";
import { interviewKeys } from "./query-keys";

export function useMatchGuestAnswers(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => interviewApi.matchAnswers(guestId),
    onSuccess: (data) => {
      queryClient.setQueryData(interviewKeys.transcript(guestId), data.transcript);
      queryClient.invalidateQueries({ queryKey: questionKeys.guest(guestId) });
    },
  });
}
