import { useMutation, useQueryClient } from "@tanstack/react-query";

import { interviewApi } from "../api/interview-api";
import { interviewKeys } from "./query-keys";

/** Manual correction only - deliberately does NOT trigger re-matching,
 * matching the backend's own PATCH /transcript behavior. */
export function useUpdateGuestTranscript(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (text: string) => interviewApi.updateTranscript(guestId, text),
    onSuccess: (data) => {
      queryClient.setQueryData(interviewKeys.transcript(guestId), data);
    },
  });
}
