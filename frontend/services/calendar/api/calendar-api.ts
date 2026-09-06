import { apiClient } from "@/lib/api/client";
import type { CalendarEvent } from "../types/calendar-event";

export const calendarApi = {
  /** start/end are "YYYY-MM-DD", inclusive on both ends. */
  listEvents: (start: string, end: string): Promise<CalendarEvent[]> =>
    apiClient.get<CalendarEvent[]>("/api/calendar/events", { query: { start, end } }),
};
