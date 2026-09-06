"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import type { CalendarDayInfo } from "../lib/date-utils";
import { formatFullDateArabic, formatTimeArabic } from "../lib/date-utils";
import type { CalendarEvent } from "../types/calendar-event";

type DayOverview = {
  day: CalendarDayInfo;
  events: CalendarEvent[];
};

type DayEventsDialogProps = {
  dayOverview: DayOverview | null;
  onOpenChange: (open: boolean) => void;
  onSelectEvent: (event: CalendarEvent) => void;
};

/** Opened from a day cell's "+N أخرى" - lists every interview scheduled
 * that day so a busy day is still easy to scan (Part: "if there are
 * multiple events in one day, handle them gracefully"). */
export function DayEventsDialog({ dayOverview, onOpenChange, onSelectEvent }: DayEventsDialogProps) {
  return (
    <Dialog open={dayOverview !== null} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-sm">
        {dayOverview ? (
          <>
            <DialogHeader>
              <DialogTitle>{formatFullDateArabic(dayOverview.day.isoDate)}</DialogTitle>
            </DialogHeader>
            <div className="flex max-h-80 flex-col gap-1.5 overflow-y-auto">
              {dayOverview.events.map((event) => (
                <button
                  key={event.id}
                  type="button"
                  onClick={() => onSelectEvent(event)}
                  className="flex items-center justify-between gap-3 rounded-xl border border-border px-3 py-2.5 text-start transition-colors hover:border-[#1B8FEA]/30 hover:bg-[#1B8FEA]/5"
                >
                  <span className="min-w-0 flex-1 truncate text-sm font-medium text-foreground">
                    {event.guest_name}
                  </span>
                  <span className="shrink-0 text-xs text-muted-foreground">{formatTimeArabic(event.time)}</span>
                </button>
              ))}
            </div>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
