/**
 * Mirrors backend/app/schemas/question.py, question_generation.py,
 * question_improvement.py, and question_version.py exactly.
 */

export type QuestionSource = "manual" | "ai_generated" | "ai_improved";
export type QuestionStatus = "draft" | "approved" | "asked" | "answered";
export type AnswerStatus = "not_answered" | "answered" | "uncertain";
export type AnswerSource = "manual" | "ai_extracted";

export type Question = {
  id: string;
  guest_id: string;
  text: string;
  source: QuestionSource;
  status: QuestionStatus;
  topic: string | null;
  category: string | null;
  priority: string | null;
  intent_summary: string | null;
  position: number;
  is_important: boolean;
  is_optional: boolean;
  notes: string | null;
  research_id: string | null;
  research_version: number | null;
  research_item_ids: string[];
  source_urls: string[];
  follow_up_questions: string[];
  generation_reason: string | null;
  generation_run_id: string | null;
  generation_candidate_id: string | null;
  // Interview-tab fields - present on the response but not surfaced by the
  // Questions workspace (that's the Interview tab's job).
  spoken_question: string | null;
  answer: string | null;
  answer_status: AnswerStatus;
  answer_source: AnswerSource | null;
  answer_updated_at: string | null;
  created_at: string;
  updated_at: string;
};

export type QuestionCreateInput = {
  text: string;
  source?: QuestionSource;
  status?: QuestionStatus;
  topic?: string | null;
  position?: number;
  is_important?: boolean;
  is_optional?: boolean;
  notes?: string | null;
};

export type QuestionUpdateInput = Partial<QuestionCreateInput>;

export type QuestionVersion = {
  id: string;
  question_id: string;
  version: number;
  text: string;
  source: QuestionSource;
  created_at: string;
};

// --- Generation ---

export type QuestionGenerationLanguage = "ar" | "en";
export type QuestionGenerationPriority = "low" | "medium" | "high";

export type QuestionGenerationRequest = {
  count: number;
  language: QuestionGenerationLanguage;
  style: string;
  include_followups: boolean;
  topics?: string[] | null;
};

export type GeneratedQuestion = {
  candidate_id: string;
  text: string;
  topic: string | null;
  category: string;
  intent_summary: string;
  priority: QuestionGenerationPriority;
  research_item_ids: string[];
  source_urls: string[];
  reason: string | null;
  follow_up_questions: string[];
};

export type QuestionGenerationResponse = {
  guest_id: string;
  generation_run_id: string;
  research_id: string;
  research_version: number;
  generator_provider: string;
  generator_model: string | null;
  requested_count: number;
  candidate_count: number;
  generated_count: number;
  duplicates_filtered_count: number;
  refill_attempts: number;
  questions: GeneratedQuestion[];
};

export type SelectedGeneratedQuestion = GeneratedQuestion;

export type QuestionGenerationSaveRequest = {
  generation_run_id: string;
  research_id: string;
  research_version: number;
  questions: GeneratedQuestion[];
};

export type SkippedGeneratedQuestion = {
  candidate_id: string | null;
  text: string;
  reason: "already_saved" | "exact_duplicate" | "semantic_duplicate" | "concurrent_duplicate";
  duplicate_of_question_id: string | null;
};

export type QuestionGenerationSaveResponse = {
  guest_id: string;
  saved_count: number;
  skipped_count: number;
  questions: Question[];
  skipped: SkippedGeneratedQuestion[];
};

// --- Improvement ---

export type QuestionImprovementLanguage = "ar" | "en";
export type QuestionImprovementStyle = "conversational" | "professional" | "deep" | "concise";
export type QuestionImprovementGoal = "clarity" | "depth" | "brevity" | "natural";

export type QuestionImprovementRequest = {
  language?: QuestionImprovementLanguage;
  style?: QuestionImprovementStyle;
  goal?: QuestionImprovementGoal;
};

export type QuestionImprovementPreview = {
  question_id: string;
  original_text: string;
  improved_text: string;
  reason: string | null;
  changes: string[];
};
