"use client";

import { Calendar as CalendarIcon, Clock, MapPin, Pencil, Trash2, User } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ApiError } from "@/lib/api/client";
import { useScheduleInterview } from "../hooks/use-schedule-interview";
import { formatFullDateArabic, formatTimeArabic } from "../lib/date-utils";
import type { CalendarEvent } from "../types/calendar-event";

type EventDetailsDialogProps = {
  event: CalendarEvent | null;
  onOpenChange: (open: boolean) => void;
  onEdit: (event: CalendarEvent) => void;
};

/** Shown when an event chip is clicked - guest name, full date, time,
 * location, and a link to the guest's own page, plus basic edit/cancel
 * actions (not "complex scheduling" - just the same PATCH the schedule
 * dialog uses, see use-schedule-interview.ts). */
export function EventDetailsDialog({ event, onOpenChange, onEdit }: EventDetailsDialogProps) {
  const [cancelOpen, setCancelOpen] = useState(false);
  const scheduleInterview = useScheduleInterview();

  async function handleCancelConfirm() {
    if (!event) return;
    try {
      await scheduleInterview.mutateAsync({ guestId: event.guest_id, scheduledAt: null, location: null });
      toast.success("تم إلغاء موعد المقابلة");
      setCancelOpen(false);
      onOpenChange(false);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "تعذر إلغاء الموعد.");
    }
  }

  return (
    <>
      <Dialog open={event !== null} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-sm">
          {event ? (
            <>
              <DialogHeader>
                <DialogTitle>{event.guest_name}</DialogTitle>
              </DialogHeader>

              <div className="space-y-3 py-1 text-sm">
                <div className="flex items-center gap-2.5 text-foreground">
                  <CalendarIcon className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
                  <span>{formatFullDateArabic(event.date)}</span>
                </div>
                <div className="flex items-center gap-2.5 text-foreground">
                  <Clock className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
                  <span>{formatTimeArabic(event.time)}</span>
                </div>
                {event.location ? (
                  <div className="flex items-center gap-2.5 text-foreground">
                    <MapPin className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
                    <span>{event.location}</span>
                  </div>
                ) : null}
                <Link
                  href={`/guests/${event.guest_id}`}
                  className="flex items-center gap-2.5 text-[#1B8FEA] hover:underline"
                >
                  <User className="size-4 shrink-0" aria-hidden="true" />
                  <span>عرض صفحة الضيف</span>
                </Link>
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  className="text-destructive hover:text-destructive"
                  onClick={() => setCancelOpen(true)}
                >
                  <Trash2 className="size-4" />
                  إلغاء الموعد
                </Button>
                <Button type="button" onClick={() => onEdit(event)}>
                  <Pencil className="size-4" />
                  تعديل
                </Button>
              </DialogFooter>
            </>
          ) : null}
        </DialogContent>
      </Dialog>

      <AlertDialog open={cancelOpen} onOpenChange={setCancelOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>إلغاء موعد المقابلة؟</AlertDialogTitle>
            <AlertDialogDescription>
              سيتم إلغاء موعد مقابلة {event?.guest_name} من التقويم. يمكنك جدولة موعد جديد لاحقًا.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>تراجع</AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              disabled={scheduleInterview.isPending}
              onClick={handleCancelConfirm}
            >
              إلغاء الموعد
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
