import { useQuery } from "@tanstack/react-query";

import { designApi } from "../api/design-api";
import { designKeys } from "./query-keys";

export function useGuestDesigns(guestId: string) {
  return useQuery({
    queryKey: designKeys.guest(guestId),
    queryFn: () => designApi.list(guestId),
    enabled: Boolean(guestId),
  });
}
