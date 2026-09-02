import { useQuery } from "@tanstack/react-query";

import { questionsApi } from "../api/questions-api";
import { questionKeys } from "./query-keys";

export function useGuestQuestions(guestId: string) {
  return useQuery({
    queryKey: questionKeys.guest(guestId),
    queryFn: () => questionsApi.list(guestId),
    enabled: Boolean(guestId),
  });
}
