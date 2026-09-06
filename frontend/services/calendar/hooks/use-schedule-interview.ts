import { useMutation, useQueryClient } from "@tanstack/react-query";

import { guestsApi } from "@/services/guests/api/guests-api";
import { guestKeys } from "@/services/guests/hooks/query-keys";
import { calendarKeys } from "./query-keys";

export type ScheduleInterviewInput = {
  guestId: string;
  /** "YYYY-MM-DDTHH:MM:00" (naive, built directly from native date/time
   * inputs - never passed through `Date`/`toISOString()`, see
   * schedule-interview-dialog.tsx) or `null` to cancel the interview. */
  scheduledAt: string | null;
  location: string | null;
};

/** Scheduling, rescheduling, and canceling a guest's interview all reuse
 * the existing guests API/PATCH endpoint - there is no separate
 * create/update/delete endpoint for calendar events (see
 * backend/app/api/calendar.py, which only exposes a read). */
export function useScheduleInterview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ guestId, scheduledAt, location }: ScheduleInterviewInput) =>
      guestsApi.update(guestId, {
        interview_scheduled_at: scheduledAt,
        interview_location: location,
      }),
    onSuccess: (_guest, variables) => {
      queryClient.invalidateQueries({ queryKey: calendarKeys.all });
      queryClient.invalidateQueries({ queryKey: guestKeys.detail(variables.guestId) });
      queryClient.invalidateQueries({ queryKey: guestKeys.lists() });
    },
  });
}
