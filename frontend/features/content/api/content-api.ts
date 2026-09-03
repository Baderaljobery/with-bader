import { apiClient } from "@/lib/api/client";
import type {
  ContentDraft,
  ContentDraftCreateInput,
  ContentDraftUpdateInput,
  ContentGenerationRequest,
  ContentGenerationResponse,
} from "../types/content";

export const contentApi = {
  generate: (
    guestId: string,
    request: ContentGenerationRequest,
  ): Promise<ContentGenerationResponse> =>
    apiClient.post<ContentGenerationResponse>(`/api/guests/${guestId}/content/generate`, request),

  list: (guestId: string): Promise<ContentDraft[]> =>
    apiClient.get<ContentDraft[]>(`/api/guests/${guestId}/content`),

  create: (guestId: string, input: ContentDraftCreateInput): Promise<ContentDraft> =>
    apiClient.post<ContentDraft>(`/api/guests/${guestId}/content`, input),

  get: (contentId: string): Promise<ContentDraft> =>
    apiClient.get<ContentDraft>(`/api/content/${contentId}`),

  update: (contentId: string, input: ContentDraftUpdateInput): Promise<ContentDraft> =>
    apiClient.patch<ContentDraft>(`/api/content/${contentId}`, input),

  remove: (contentId: string): Promise<void> =>
    apiClient.delete<void>(`/api/content/${contentId}`),

  approve: (contentId: string): Promise<ContentDraft> =>
    apiClient.post<ContentDraft>(`/api/content/${contentId}/approve`),
};
