import { apiClient } from "@/lib/api/client";
import type { GuestResearch, GuestResearchRunResponse } from "../types/research";

export const researchApi = {
  getLatest: (guestId: string): Promise<GuestResearch> =>
    apiClient.get<GuestResearch>(`/api/guests/${guestId}/research/latest`),

  getHistory: (guestId: string): Promise<GuestResearch[]> =>
    apiClient.get<GuestResearch[]>(`/api/guests/${guestId}/research`),

  getById: (researchId: string): Promise<GuestResearch> =>
    apiClient.get<GuestResearch>(`/api/guest-research/${researchId}`),

  run: (guestId: string): Promise<GuestResearchRunResponse> =>
    apiClient.post<GuestResearchRunResponse>(`/api/guests/${guestId}/research/run`),
};
