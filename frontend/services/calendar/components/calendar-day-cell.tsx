"use client";

import { cn } from "@/lib/utils";
import type { CalendarDayInfo } from "../lib/date-utils";
import type { CalendarEvent } from "../types/calendar-event";
import { EventChip } from "./event-chip";

const MAX_VISIBLE_EVENTS = 2;

type CalendarDayCellProps = {
  day: CalendarDayInfo;
  events: CalendarEvent[];
  isLastColumn: boolean;
  isLastRow: boolean;
  onSelectEvent: (event: CalendarEvent) => void;
  onShowMore: (day: CalendarDayInfo, events: CalendarEvent[]) => void;
};

export function CalendarDayCell({
  day,
  events,
  isLastColumn,
  isLastRow,
  onSelectEvent,
  onShowMore,
}: CalendarDayCellProps) {
  const visible = events.slice(0, MAX_VISIBLE_EVENTS);
  const hiddenCount = events.length - visible.length;

  return (
    <div
      className={cn(
        "flex min-h-[92px] flex-col gap-1 border-border p-1.5 sm:min-h-[120px] sm:p-2",
        !isLastRow && "border-b",
        !isLastColumn && "border-e",
        !day.inCurrentMonth && "bg-secondary/30",
      )}
    >
      <span
        className={cn(
          "flex size-6 shrink-0 items-center justify-center rounded-full text-xs font-medium",
          day.isToday
            ? "bg-[image:var(--gradient-primary)] text-white"
            : day.inCurrentMonth
              ? "text-foreground"
              : "text-muted-foreground/50",
        )}
      >
        {day.date.getDate()}
      </span>

      {events.length > 0 ? (
        <div className="flex flex-col gap-1">
          {visible.map((event) => (
            <EventChip key={event.id} event={event} onClick={() => onSelectEvent(event)} />
          ))}
          {hiddenCount > 0 ? (
            <button
              type="button"
              onClick={() => onShowMore(day, events)}
              className="rounded-md px-1.5 py-0.5 text-start text-[11px] font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            >
              +{hiddenCount} أخرى
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
