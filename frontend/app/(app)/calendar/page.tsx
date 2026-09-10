"use client";

import { Plus } from "lucide-react";
import { useMemo, useState } from "react";

import { AnimatedLogo } from "@/components/brand/animated-logo";
import { ErrorState } from "@/components/shared/error-state";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { CalendarGrid } from "@/services/calendar/components/calendar-grid";
import { CalendarToolbar } from "@/services/calendar/components/calendar-toolbar";
import { DayEventsDialog } from "@/services/calendar/components/day-events-dialog";
import { EventDetailsDialog } from "@/services/calendar/components/event-details-dialog";
import { ScheduleInterviewDialog } from "@/services/calendar/components/schedule-interview-dialog";
import { useCalendarEvents } from "@/services/calendar/hooks/use-calendar-events";
import { getMonthGrid, type CalendarDayInfo } from "@/services/calendar/lib/date-utils";
import type { CalendarEvent } from "@/services/calendar/types/calendar-event";

type DayOverview = { day: CalendarDayInfo; events: CalendarEvent[] };
type ScheduleDialogState = { open: boolean; event?: CalendarEvent };

export default function CalendarPage() {
  const today = useMemo(() => new Date(), []);
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth());

  const days = useMemo(() => getMonthGrid(viewYear, viewMonth), [viewYear, viewMonth]);
  const rangeStart = days[0].isoDate;
  const rangeEnd = days[days.length - 1].isoDate;

  const { data: events, isPending, isFetching, isError, refetch } = useCalendarEvents(rangeStart, rangeEnd);

  const eventsByDate = useMemo(() => {
    const map = new Map<string, CalendarEvent[]>();
    for (const event of events ?? []) {
      const list = map.get(event.date) ?? [];
      list.push(event);
      map.set(event.date, list);
    }
    return map;
  }, [events]);

  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [dayOverview, setDayOverview] = useState<DayOverview | null>(null);
  const [scheduleDialog, setScheduleDialog] = useState<ScheduleDialogState>({ open: false });

  function goToPrevMonth() {
    setViewMonth((month) => {
      if (month === 0) {
        setViewYear((year) => year - 1);
        return 11;
      }
      return month - 1;
    });
  }

  function goToNextMonth() {
    setViewMonth((month) => {
      if (month === 11) {
        setViewYear((year) => year + 1);
        return 0;
      }
      return month + 1;
    });
  }

  function goToToday() {
    setViewYear(today.getFullYear());
    setViewMonth(today.getMonth());
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="التقويم"
        description="تابع مواعيد المقابلات القادمة بنظرة واحدة."
        action={
          <Button onClick={() => setScheduleDialog({ open: true })}>
            <Plus className="size-4" />
            جدولة مقابلة
          </Button>
        }
      />

      <CalendarToolbar
        year={viewYear}
        month={viewMonth}
        onPrevMonth={goToPrevMonth}
        onNextMonth={goToNextMonth}
        onToday={goToToday}
      />

      {isError ? (
        <ErrorState description="تعذر تحميل مواعيد المقابلات." onRetry={() => refetch()} />
      ) : isPending ? (
        <div className="flex items-center justify-center rounded-2xl border border-dashed border-border bg-secondary/30 py-24">
          <AnimatedLogo markOnly className="size-12" />
        </div>
      ) : (
        <CalendarGrid
          days={days}
          eventsByDate={eventsByDate}
          isRefreshing={isFetching}
          onSelectEvent={setSelectedEvent}
          onShowMore={(day, dayEvents) => setDayOverview({ day, events: dayEvents })}
        />
      )}

      <EventDetailsDialog
        event={selectedEvent}
        onOpenChange={(open) => {
          if (!open) setSelectedEvent(null);
        }}
        onEdit={(event) => {
          setSelectedEvent(null);
          setScheduleDialog({ open: true, event });
        }}
      />

      <DayEventsDialog
        dayOverview={dayOverview}
        onOpenChange={(open) => {
          if (!open) setDayOverview(null);
        }}
        onSelectEvent={(event) => {
          setDayOverview(null);
          setSelectedEvent(event);
        }}
      />

      <ScheduleInterviewDialog
        open={scheduleDialog.open}
        event={scheduleDialog.event}
        onOpenChange={(open) => setScheduleDialog((current) => ({ ...current, open }))}
      />
    </div>
  );
}
