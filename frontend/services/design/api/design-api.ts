import { apiClient } from "@/lib/api/client";
import type { Block } from "@/services/notebook/types/block";
import type {
  DesignCreateRequest,
  DesignDraft,
  DesignDraftUpdateInput,
  DesignPlanRequest,
  DesignPlanResponse,
  DesignSlide,
  DesignSlideUpdateInput,
} from "../types/design";

/** No `generate`/`regenerate-all`/`slides/{i}/regenerate` calls here -
 * templates are rendered deterministically by frontend code, not by an AI
 * image model. Those backend endpoints (and the OpenRouter/Gemini image
 * generator behind them) have been removed entirely (2026-09-06 cleanup). */
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
