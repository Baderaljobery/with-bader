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

export type ContentStatus = "not_started" | "in_progress" | "published";

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
  // False when content_status is still derived automatically from the
  // Calendar (interview_scheduled_at) - true once the user has explicitly
  // picked a status themselves. See backend/app/services/guest_service.py.
  content_status_manual: boolean;
  // Calendar feature: at most one scheduled interview per guest. Naive
  // "YYYY-MM-DDTHH:MM:SS" (no timezone/offset) - see
  // backend/app/models/guest.py.
  interview_scheduled_at: string | null;
  interview_location: string | null;
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
  interview_scheduled_at?: string | null;
  interview_location?: string | null;
};

export type GuestUpdateInput = Partial<GuestCreateInput> & {
  // Send `false` on its own (no content_status) to clear a manual override
  // and let the automatic Calendar-derived status take back over.
  content_status_manual?: boolean;
};
