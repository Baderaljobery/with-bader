/**
 * Mirrors backend/app/schemas/guest_research.py, backend/app/schemas/research_engine.py,
 * and the item shapes actually persisted by backend/app/research/extraction/groq_models.py +
 * groq_postprocess.py. The backend's own Pydantic schema types these item lists as
 * `list[Any]` (extractor-dependent), so every field here is optional/nullable to match
 * what different extractors (mock vs groq) actually produce - never invented.
 */

export type ResearchSource = {
  type: string;
  url?: string | null;
  title?: string | null;
  publisher?: string | null;
  published_at?: string | null;
  snippet?: string | null;
  content?: string | null;
  provider?: string | null;
  score?: number | null;
  query?: string | null;
  notes?: string | null;
};

export type CareerHistoryItem = {
  company?: string | null;
  role?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  description?: string | null;
  source_ids?: string[];
  source_urls?: string[];
  confidence?: number | null;
};

export type EducationItem = {
  institution?: string | null;
  degree?: string | null;
  field?: string | null;
  year?: number | null;
  source_ids?: string[];
  source_urls?: string[];
  confidence?: number | null;
};

export type AchievementItem = {
  title: string;
  description?: string | null;
  date?: string | null;
  source_ids?: string[];
  source_urls?: string[];
  confidence?: number | null;
};

export type ProjectItem = {
  title: string;
  description?: string | null;
  role?: string | null;
  source_ids?: string[];
  source_urls?: string[];
  confidence?: number | null;
};

export type InterestingEventItem = {
  title: string;
  description?: string | null;
  date?: string | null;
  why_interesting?: string | null;
  source_ids?: string[];
  source_urls?: string[];
  confidence?: number | null;
};

export type InterviewAnglePriority = "low" | "medium" | "high";

export type InterviewAngleItem = {
  title: string;
  reason: string;
  priority?: InterviewAnglePriority;
  source_ids?: string[];
  source_urls?: string[];
};

export type GuestResearch = {
  id: string;
  guest_id: string;
  version: number;
  role_title: string | null;
  company: string | null;
  career_history: CareerHistoryItem[];
  education: EducationItem[];
  achievements: AchievementItem[];
  projects: ProjectItem[];
  topics: string[];
  interesting_events: InterestingEventItem[];
  potential_interview_angles: InterviewAngleItem[];
  sources: ResearchSource[];
  raw_ai_response: unknown;
  created_at: string;
};

export type GuestResearchRunResponse = {
  research_id: string;
  guest_id: string;
  version: number;
  search_provider: string;
  primary_search_provider: string;
  fallback_search_provider: string | null;
  fallback_queries_used: number;
  extractor_provider: string;
  extractor_model: string | null;
  queries_executed: number;
  queries_failed: number;
  total_sources_found: number;
  total_sources_after_deduplication: number;
  research: GuestResearch;
};
