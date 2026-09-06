import { useQuery } from "@tanstack/react-query";

import { notebookApi } from "../api/notebook-api";
import { notebookKeys } from "./query-keys";

export function useGuestNotebooks(guestId: string) {
  return useQuery({
    queryKey: notebookKeys.guest(guestId),
    queryFn: () => notebookApi.list(guestId),
    enabled: Boolean(guestId),
  });
}
