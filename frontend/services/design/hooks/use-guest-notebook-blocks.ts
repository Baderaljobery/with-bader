import { useQuery } from "@tanstack/react-query";

import { designApi } from "../api/design-api";

export function useGuestNotebookBlocks(guestId: string) {
  return useQuery({
    queryKey: ["design", "guest-notebook-blocks", guestId] as const,
    queryFn: () => designApi.listGuestNotebookBlocks(guestId),
    enabled: Boolean(guestId),
  });
}
