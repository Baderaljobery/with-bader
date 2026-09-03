/**
 * Mirrors backend/app/schemas/guest.py. Keep in sync with that file - the
 * backend is the source of truth for these fields and literals.
 */
export type PreparationStatus =
  | "not_started"
  | "researching"
  | "questions_ready"
  | "interview_scheduled"
  | "interview_completed";

export type ContentStatus = "not_started" | "in_progress" | "review" | "published";

export type Guest = {
  id: string;
  name: string;
  slug: string | null;
  job_title: string | null;
  company: string | null;
  biography: string | null;
  personal_notes: string | null;
  research_summary: string | null;
  preparation_status: PreparationStatus;
  content_status: ContentStatus;
  created_by: string | null;
  photo_id: string | null;
  created_at: string;
  updated_at: string;
};

export type GuestCreateInput = {
  name: string;
  slug?: string | null;
  job_title?: string | null;
  company?: string | null;
  biography?: string | null;
  personal_notes?: string | null;
  research_summary?: string | null;
  preparation_status?: PreparationStatus;
  content_status?: ContentStatus;
};

export type GuestUpdateInput = Partial<GuestCreateInput>;
