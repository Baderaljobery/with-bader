import { useQuery } from "@tanstack/react-query";

import { contentApi } from "../api/content-api";
import { contentKeys } from "./query-keys";

export function useGuestContent(guestId: string) {
  return useQuery({
    queryKey: contentKeys.guest(guestId),
    queryFn: () => contentApi.list(guestId),
    enabled: Boolean(guestId),
  });
}
