import type { ContentStatus } from "../types/guest";

/** Single copy of the 3 content-status labels, shared by every place that
 * displays guest.content_status (Guest Overview's select, the guest list
 * card's badge, ...) - never re-derive this from Calendar state client-side,
 * content_status/content_status_manual from the backend are the source of
 * truth (see backend/app/services/guest_service.py). */
export const CONTENT_STATUS_LABELS: Record<ContentStatus, string> = {
  not_started: "لم يبدأ",
  in_progress: "قيد التنفيذ",
  published: "تم النشر",
};
