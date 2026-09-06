/** Mirrors backend/app/schemas/content_draft.py and content_generation.py
 * exactly. */

export type ContentPlatform = "linkedin" | "x" | "instagram" | "general";
export type ContentLength = "short" | "medium" | "detailed";
export type ContentStatus = "draft" | "approved";
export type ContentSourceCategory = "answers" | "notebook" | "transcript" | "research" | "questions";
export type ContentGenerationLanguage = "ar" | "en";

export type ContentDraft = {
  id: string;
  guest_id: string;
  platform: ContentPlatform;
  length: ContentLength;
  title: string | null;
  content: string;
  status: ContentStatus;
  source_context: ContentSourceCategory[];
  ai_provider: string | null;
  ai_model: string | null;
  created_at: string;
  updated_at: string;
};

export type ContentDraftCreateInput = {
  platform: ContentPlatform;
  length: ContentLength;
  title?: string | null;
  content: string;
  source_context?: ContentSourceCategory[];
  ai_provider?: string | null;
  ai_model?: string | null;
};

export type ContentDraftUpdateInput = Partial<{
  platform: ContentPlatform;
  length: ContentLength;
  title: string | null;
  content: string;
  status: ContentStatus;
}>;

export type ContentGenerationRequest = {
  platform: ContentPlatform;
  length: ContentLength;
  language?: ContentGenerationLanguage;
  custom_instructions?: string | null;
};

/** Preview only - never persisted until the frontend explicitly calls
 * contentApi.create/update (see hooks/use-save-content.ts). */
export type ContentGenerationResponse = {
  guest_id: string;
  platform: ContentPlatform;
  length: ContentLength;
  language: ContentGenerationLanguage;
  title: string | null;
  content: string;
  sources_used: ContentSourceCategory[];
  ai_provider: string;
  ai_model: string | null;
};
