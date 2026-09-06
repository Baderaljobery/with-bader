import { useQuery } from "@tanstack/react-query";

import { guestsApi } from "../api/guests-api";
import { guestKeys } from "./query-keys";

export function useGuests() {
  return useQuery({
    queryKey: guestKeys.lists(),
    queryFn: guestsApi.list,
  });
}
