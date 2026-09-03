import { apiClient } from "@/lib/api/client";
import type { Block } from "@/features/notebook/types/block";
import type {
  DesignCreateRequest,
  DesignDraft,
  DesignDraftUpdateInput,
  DesignPlanRequest,
  DesignPlanResponse,
  DesignSlide,
  DesignSlideUpdateInput,
} from "../types/design";

/** No `generate`/`regenerate-all`/`slides/{i}/regenerate` calls here on
 * purpose - the strict template-renderer flow never calls the AI
 * image-generation endpoints (Part 16/30 of the Design Engine rework:
 * templates are rendered deterministically by frontend code, not by
 * Gemini/OpenRouter). Those backend endpoints still exist for a possible
 * future legacy/creative path (Part 31) but are intentionally unused here. */
export const designApi = {
  list: (guestId: string): Promise<DesignDraft[]> =>
    apiClient.get<DesignDraft[]>(`/api/guests/${guestId}/designs`),

  plan: (guestId: string, request: DesignPlanRequest): Promise<DesignPlanResponse> =>
    apiClient.post<DesignPlanResponse>(`/api/guests/${guestId}/designs/plan`, request),

  create: (guestId: string, request: DesignCreateRequest): Promise<DesignDraft> =>
    apiClient.post<DesignDraft>(`/api/guests/${guestId}/designs`, request),

  get: (designId: string): Promise<DesignDraft> =>
    apiClient.get<DesignDraft>(`/api/designs/${designId}`),

  update: (designId: string, input: DesignDraftUpdateInput): Promise<DesignDraft> =>
    apiClient.patch<DesignDraft>(`/api/designs/${designId}`, input),

  remove: (designId: string): Promise<void> => apiClient.delete<void>(`/api/designs/${designId}`),

  updateSlide: (designId: string, slideIndex: number, input: DesignSlideUpdateInput): Promise<DesignSlide> =>
    apiClient.patch<DesignSlide>(`/api/designs/${designId}/slides/${slideIndex}`, input),

  listGuestNotebookBlocks: (guestId: string): Promise<Block[]> =>
    apiClient.get<Block[]>(`/api/guests/${guestId}/notebook-blocks`),
};
