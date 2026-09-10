import { useQuery } from "@tanstack/react-query";

import { guestLinksApi } from "../api/guest-links-api";
import { guestKeys } from "./query-keys";

export function useGuestLinks(guestId: string) {
  return useQuery({
    queryKey: guestKeys.links(guestId),
    queryFn: () => guestLinksApi.list(guestId),
    enabled: Boolean(guestId),
  });
}
