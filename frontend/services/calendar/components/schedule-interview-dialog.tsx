"use client";

import { useState, type FormEvent } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useGuests } from "@/services/guests/hooks/use-guests";
import { ApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/format-date";
import { useScheduleInterview } from "../hooks/use-schedule-interview";
import type { CalendarEvent } from "../types/calendar-event";

type ScheduleInterviewDialogProps = {
  open: boolean;
  /** Present when rescheduling/editing an existing event - the guest is
   * then fixed (not re-selectable), only date/time/location can change. */
  event?: CalendarEvent;
  onOpenChange: (open: boolean) => void;
};

/** Wraps the actual form in a component keyed by which event (if any) is
 * being edited, so switching between "add" and "edit for event X" (or
 * between two different events) remounts fresh initial state instead of
 * resetting it in an effect. */
export function ScheduleInterviewDialog({ open, event, onOpenChange }: ScheduleInterviewDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <ScheduleInterviewForm key={open ? (event?.id ?? "new") : "closed"} event={event} onOpenChange={onOpenChange} />
      </DialogContent>
    </Dialog>
  );
}

type ScheduleInterviewFormProps = {
  event?: CalendarEvent;
  onOpenChange: (open: boolean) => void;
};

/** "Add Event" and "Edit" share this one form (same pattern as
 * GuestFormDialog's isEdit flag) - both just call the same PATCH under
 * the hood via useScheduleInterview. */
function ScheduleInterviewForm({ event, onOpenChange }: ScheduleInterviewFormProps) {
  const isEdit = Boolean(event);
  const { data: guests } = useGuests();
  const scheduleInterview = useScheduleInterview();

  const [guestId, setGuestId] = useState(event?.guest_id ?? "");
  const [date, setDate] = useState(event?.date ?? "");
  const [time, setTime] = useState(event?.time ?? "");
  const [location, setLocation] = useState(event?.location ?? "");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(formEvent: FormEvent) {
    formEvent.preventDefault();
    if (!guestId) {
      setError("اختر الضيف");
      return;
    }
    if (!date || !time) {
      setError("التاريخ والوقت مطلوبان");
      return;
    }
    setError(null);

    try {
      // Native date/time inputs already produce "YYYY-MM-DD"/"HH:MM" - no
      // Date()/toISOString() conversion anywhere in this path (see
      // use-schedule-interview.ts for why that matters here).
      await scheduleInterview.mutateAsync({
        guestId,
        scheduledAt: `${date}T${time}:00`,
        location: location.trim() || null,
      });
      toast.success(isEdit ? "تم تحديث موعد المقابلة" : "تمت جدولة المقابلة");
      onOpenChange(false);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "حدث خطأ ما.");
    }
  }

  const selectedGuestName = guests?.find((guest) => guest.id === guestId)?.name;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <DialogHeader>
        <DialogTitle>{isEdit ? "تعديل موعد المقابلة" : "جدولة مقابلة"}</DialogTitle>
        <DialogDescription>
          {isEdit ? "حدّث تاريخ أو وقت أو موقع هذه المقابلة." : "اختر الضيف وحدد موعد مقابلته."}
        </DialogDescription>
      </DialogHeader>

      <div className="space-y-1.5">
        <Label htmlFor="schedule-guest">الضيف</Label>
        {isEdit ? (
          <Input id="schedule-guest" value={event?.guest_name ?? ""} disabled />
        ) : (
          <Select value={guestId} onValueChange={(value) => setGuestId(value ?? "")}>
            <SelectTrigger id="schedule-guest" className="w-full">
              <SelectValue placeholder="اختر ضيفًا">{() => selectedGuestName ?? "اختر ضيفًا"}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {(guests ?? []).map((guest) => (
                <SelectItem key={guest.id} value={guest.id}>
                  {guest.name}
                  {guest.interview_scheduled_at
                    ? ` (مجدولة سابقًا: ${formatDate(guest.interview_scheduled_at)})`
                    : ""}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="schedule-date">التاريخ</Label>
          <Input
            id="schedule-date"
            type="date"
            value={date}
            onChange={(changeEvent) => setDate(changeEvent.target.value)}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="schedule-time">الوقت</Label>
          <Input
            id="schedule-time"
            type="time"
            value={time}
            onChange={(changeEvent) => setTime(changeEvent.target.value)}
          />
        </div>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="schedule-location">الموقع</Label>
        <Input
          id="schedule-location"
          placeholder="مثال: مكتب الرياض، مكالمة عبر Zoom"
          value={location}
          onChange={(changeEvent) => setLocation(changeEvent.target.value)}
        />
      </div>

      {error ? <p className="text-xs text-destructive">{error}</p> : null}

      <DialogFooter>
        <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
          إلغاء
        </Button>
        <Button type="submit" disabled={scheduleInterview.isPending}>
          {scheduleInterview.isPending ? "جارٍ الحفظ..." : isEdit ? "حفظ التغييرات" : "جدولة المقابلة"}
        </Button>
      </DialogFooter>
    </form>
  );
}
