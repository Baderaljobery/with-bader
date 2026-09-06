import { useQuery } from "@tanstack/react-query";

import { guestsApi } from "../api/guests-api";
import { guestKeys } from "./query-keys";

export function useGuest(guestId: string) {
  return useQuery({
    queryKey: guestKeys.detail(guestId),
    queryFn: () => guestsApi.get(guestId),
    enabled: Boolean(guestId),
  });
}
