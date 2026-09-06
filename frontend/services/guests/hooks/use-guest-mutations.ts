import { useMutation, useQueryClient } from "@tanstack/react-query";

import { guestsApi } from "../api/guests-api";
import type { GuestCreateInput, GuestUpdateInput } from "../types/guest";
import { guestKeys } from "./query-keys";

export function useCreateGuest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: GuestCreateInput) => guestsApi.create(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: guestKeys.lists() });
    },
  });
}

export function useUpdateGuest(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: GuestUpdateInput) => guestsApi.update(guestId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: guestKeys.lists() });
      queryClient.invalidateQueries({ queryKey: guestKeys.detail(guestId) });
    },
  });
}

export function useDeleteGuest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (guestId: string) => guestsApi.remove(guestId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: guestKeys.lists() });
    },
  });
}
