/** Mirrors backend/app/schemas/calendar.py exactly. A calendar "event" is
 * just a guest with a scheduled interview - there is no separate events
 * table or endpoint for create/update/delete (see calendar-api.ts, which
 * reuses the existing guests API for writes). */
export type CalendarEvent = {
  id: string;
  guest_id: string;
  guest_name: string;
  /** "YYYY-MM-DD" */
  date: string;
  /** "HH:MM", 24h */
  time: string;
  location: string | null;
};
