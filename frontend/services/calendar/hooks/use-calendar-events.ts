import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { calendarApi } from "../api/calendar-api";
import { calendarKeys } from "./query-keys";

/** Keeps the previous month's events visible (via `placeholderData`) while
 * the next range loads, instead of flashing an empty grid on every month
 * navigation - the page dims the grid slightly during that refetch. */
export function useCalendarEvents(start: string, end: string) {
  return useQuery({
    queryKey: calendarKeys.events(start, end),
    queryFn: () => calendarApi.listEvents(start, end),
    placeholderData: keepPreviousData,
  });
}
