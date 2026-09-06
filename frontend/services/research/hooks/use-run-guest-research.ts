import { useMutation, useQueryClient } from "@tanstack/react-query";

import { researchApi } from "../api/research-api";
import { researchKeys } from "./query-keys";

export function useRunGuestResearch(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => researchApi.run(guestId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: researchKeys.latest(guestId) });
      queryClient.invalidateQueries({ queryKey: researchKeys.history(guestId) });
    },
  });
}
