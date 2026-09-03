import { useMutation, useQueryClient } from "@tanstack/react-query";

import { questionKeys } from "@/features/questions/hooks/query-keys";
import { interviewApi } from "../api/interview-api";
import { interviewKeys } from "./query-keys";

export function useTranscribeGuestInterview(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, replaceExisting }: { file: File; replaceExisting: boolean }) =>
      interviewApi.transcribe(guestId, file, replaceExisting),
    onSuccess: (data) => {
      queryClient.setQueryData(interviewKeys.transcript(guestId), data.transcript);
      queryClient.invalidateQueries({ queryKey: questionKeys.guest(guestId) });
    },
  });
}
