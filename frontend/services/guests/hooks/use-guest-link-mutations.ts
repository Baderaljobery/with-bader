import { useMutation, useQueryClient } from "@tanstack/react-query";

import { guestLinksApi } from "../api/guest-links-api";
import type { GuestLinkCreateInput, GuestLinkUpdateInput } from "../types/guest-link";
import { guestKeys } from "./query-keys";

export function useCreateGuestLink(guestId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: GuestLinkCreateInput) => guestLinksApi.create(guestId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: guestKeys.links(guestId) });
    },
  });
}

export function useUpdateGuestLink(guestId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ linkId, input }: { linkId: string; input: GuestLinkUpdateInput }) =>
      guestLinksApi.update(linkId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: guestKeys.links(guestId) });
    },
  });
}

export function useDeleteGuestLink(guestId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (linkId: string) => guestLinksApi.remove(linkId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: guestKeys.links(guestId) });
    },
  });
}
