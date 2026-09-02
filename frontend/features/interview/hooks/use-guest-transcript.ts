import { useQuery } from "@tanstack/react-query";

import { interviewApi } from "../api/interview-api";
import { interviewKeys } from "./query-keys";

export function useGuestTranscript(guestId: string) {
  return useQuery({
    queryKey: interviewKeys.transcript(guestId),
    queryFn: () => interviewApi.getTranscript(guestId),
    enabled: Boolean(guestId),
  });
}
