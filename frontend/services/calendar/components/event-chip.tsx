"use client";

import { formatTimeArabic } from "../lib/date-utils";
import type { CalendarEvent } from "../types/calendar-event";

type EventChipProps = {
  event: CalendarEvent;
  onClick: () => void;
};

export function EventChip({ event, onClick }: EventChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full items-center gap-1.5 rounded-md border border-transparent bg-secondary px-1.5 py-1 text-start transition-colors hover:border-[#1B8FEA]/30 hover:bg-[#1B8FEA]/8"
    >
      <span
        className="size-1.5 shrink-0 rounded-full"
        style={{ backgroundImage: "var(--gradient-primary)" }}
        aria-hidden="true"
      />
      <span className="min-w-0 flex-1 truncate text-[11px] font-medium text-foreground">
        {event.guest_name}
      </span>
      <span className="shrink-0 text-[10px] text-muted-foreground">{formatTimeArabic(event.time)}</span>
    </button>
  );
}
