"use client";

import { cn } from "@/lib/utils";
import type { CalendarDayInfo } from "../lib/date-utils";
import { WEEKDAY_LABELS } from "../lib/labels";
import type { CalendarEvent } from "../types/calendar-event";
import { CalendarDayCell } from "./calendar-day-cell";

type CalendarGridProps = {
  days: CalendarDayInfo[];
  eventsByDate: Map<string, CalendarEvent[]>;
  isRefreshing?: boolean;
  onSelectEvent: (event: CalendarEvent) => void;
  onShowMore: (day: CalendarDayInfo, events: CalendarEvent[]) => void;
};

export function CalendarGrid({ days, eventsByDate, isRefreshing, onSelectEvent, onShowMore }: CalendarGridProps) {
  return (
    <div
      className={cn(
        "overflow-hidden rounded-2xl border border-border shadow-[var(--shadow-soft)] transition-opacity",
        isRefreshing && "opacity-60",
      )}
      style={{ backgroundImage: "var(--surface-tint)" }}
    >
      <div className="grid grid-cols-7 border-b border-border bg-secondary/40">
        {WEEKDAY_LABELS.map((label) => (
          <div
            key={label}
            className="border-e border-border px-1 py-2.5 text-center text-xs font-medium text-muted-foreground last:border-e-0"
          >
            {label}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7">
        {days.map((day, index) => (
          <CalendarDayCell
            key={day.isoDate}
            day={day}
            events={eventsByDate.get(day.isoDate) ?? []}
            isLastColumn={index % 7 === 6}
            isLastRow={index >= days.length - 7}
            onSelectEvent={onSelectEvent}
            onShowMore={onShowMore}
          />
        ))}
      </div>
    </div>
  );
}
