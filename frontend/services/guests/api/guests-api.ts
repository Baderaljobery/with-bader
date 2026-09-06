import { apiClient } from "@/lib/api/client";
import type { Guest, GuestCreateInput, GuestUpdateInput } from "../types/guest";

export const guestsApi = {
  list: (): Promise<Guest[]> => apiClient.get<Guest[]>("/api/guests"),

  get: (guestId: string): Promise<Guest> =>
    apiClient.get<Guest>(`/api/guests/${guestId}`),

  create: (input: GuestCreateInput): Promise<Guest> =>
    apiClient.post<Guest>("/api/guests", input),

  update: (guestId: string, input: GuestUpdateInput): Promise<Guest> =>
    apiClient.patch<Guest>(`/api/guests/${guestId}`, input),

  remove: (guestId: string): Promise<void> =>
    apiClient.delete<void>(`/api/guests/${guestId}`),
};
