import { apiClient } from "@/lib/api/client";
import type { GuestLink, GuestLinkCreateInput, GuestLinkUpdateInput } from "../types/guest-link";

export const guestLinksApi = {
  list: (guestId: string): Promise<GuestLink[]> =>
    apiClient.get<GuestLink[]>(`/api/guests/${guestId}/links`),

  create: (guestId: string, input: GuestLinkCreateInput): Promise<GuestLink> =>
    apiClient.post<GuestLink>(`/api/guests/${guestId}/links`, input),

  update: (linkId: string, input: GuestLinkUpdateInput): Promise<GuestLink> =>
    apiClient.patch<GuestLink>(`/api/guest-links/${linkId}`, input),

  remove: (linkId: string): Promise<void> =>
    apiClient.delete<void>(`/api/guest-links/${linkId}`),
};
