/** Mirrors backend/app/schemas/design_draft.py, design_slide.py, and
 * design_generation.py exactly. The generation prompt is never exposed to
 * the frontend. */

export type DesignPlatform = "linkedin" | "x" | "instagram" | "general";
export type DesignStatus = "draft" | "approved";
export type DesignAspectRatio = "1:1" | "4:5" | "16:9" | "9:16";
export type SlideRole = "cover" | "main_content" | "continuation" | "quote" | "quick_points" | "closing";

export type DesignSlide = {
  id: string;
  design_draft_id: string;
  slide_index: number;
  role: SlideRole;
  headline: string;
  body_text: string;
  cta_text: string | null;
  image_path: string | null;
  created_at: string;
  updated_at: string;
};

export type DesignDraft = {
  id: string;
  guest_id: string;
  content_draft_id: string | null;
  title: string | null;
  platform: DesignPlatform;
  status: DesignStatus;
  template_id: string;
  slide_count: number;
  aspect_ratio: DesignAspectRatio;
  background_color: string;
  accent_color: string;
  customizations: Record<string, unknown>;
  ai_provider: string | null;
  ai_model: string | null;
  slides: DesignSlide[];
  created_at: string;
  updated_at: string;
};

export type DesignDraftUpdateInput = Partial<{
  title: string | null;
  background_color: string;
  accent_color: string;
  status: DesignStatus;
}>;

export type DesignSlideUpdateInput = Partial<{
  headline: string;
  body_text: string;
  cta_text: string | null;
}>;

// --- Planning (step 1 - preview, nothing persisted) ---

export type SlideRoleAssignment = {
  index: number;
  role: SlideRole;
};

export type DesignPlanRequest = {
  content_draft_id?: string | null;
  question_ids?: string[];
  notebook_block_ids?: string[];
  template_id: string;
  slide_count: number;
  slide_roles: SlideRoleAssignment[];
  platform: DesignPlatform;
  custom_instructions?: string | null;
};

export type PlannedSlide = {
  index: number;
  role: SlideRole;
  headline: string;
  body_text: string;
  cta_text: string | null;
};

export type DesignPlanResponse = {
  guest_id: string;
  template_id: string;
  slide_count: number;
  slides: PlannedSlide[];
  sources_used: string[];
  ai_provider: string;
  ai_model: string | null;
};

// --- Create (step 2 - persists the approved structure, no images yet) ---

export type DesignSlideInput = {
  index: number;
  role: SlideRole;
  headline: string;
  body_text: string;
  cta_text?: string | null;
};

export type DesignCreateRequest = {
  content_draft_id?: string | null;
  question_ids?: string[];
  notebook_block_ids?: string[];
  template_id: string;
  slide_count: number;
  slides: DesignSlideInput[];
  platform: DesignPlatform;
  aspect_ratio?: DesignAspectRatio;
  title?: string | null;
  custom_instructions?: string | null;
};
