import { Layers } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { useUpdateGuest } from "../hooks/use-guest-mutations";
import { CONTENT_STATUS_LABELS } from "../lib/content-status-labels";
import type { ContentStatus, Guest } from "../types/guest";

// Subtle badge-style tones only - no saturated traffic-light colors.
const CONTENT_STATUS_TRIGGER_STYLES: Record<ContentStatus, string> = {
  not_started: "border-transparent bg-secondary text-muted-foreground",
  in_progress: "border-transparent bg-[#1B8FEA]/10 text-[#1B8FEA]",
  published: "border-transparent bg-emerald-50 text-emerald-700",
};

/** Guest Overview's compact "حالة المحتوى" control (Content Status). A
 * simple 3-state field that is auto-derived from the Calendar (see
 * guest_service._auto_content_status) until the user picks a value here,
 * at which point that manual choice takes over - see
 * backend/app/services/guest_service.py:update_guest for the full rule. */
export function ContentStatusSelect({ guest }: { guest: Guest }) {
  const { mutate: updateGuest, isPending } = useUpdateGuest(guest.id);

  return (
    <Card size="sm">
      <CardContent className="flex items-center gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[image:var(--gradient-primary)] text-white shadow-[0_6px_14px_-4px_rgba(27,143,234,0.4)]">
          <Layers className="size-4.5" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1 space-y-1">
          <p className="text-xs text-[#5F6368]">حالة المحتوى</p>
          <div className="flex items-center gap-1.5">
            <Select
              value={guest.content_status}
              onValueChange={(value) =>
                updateGuest({ content_status: value as ContentStatus })
              }
              disabled={isPending}
            >
              <SelectTrigger
                size="sm"
                className={cn(
                  "h-6.5 font-medium",
                  CONTENT_STATUS_TRIGGER_STYLES[guest.content_status]
                )}
              >
                <SelectValue>
                  {(selected: ContentStatus) => CONTENT_STATUS_LABELS[selected]}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {(Object.keys(CONTENT_STATUS_LABELS) as ContentStatus[]).map((status) => (
                  <SelectItem key={status} value={status}>
                    {CONTENT_STATUS_LABELS[status]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {!guest.content_status_manual ? (
              <span className="text-[10px] text-muted-foreground">تلقائي</span>
            ) : null}
          </div>
          {guest.content_status_manual ? (
            <button
              type="button"
              className="text-[10px] text-muted-foreground underline decoration-dotted underline-offset-2 hover:text-foreground"
              disabled={isPending}
              onClick={() => updateGuest({ content_status_manual: false })}
            >
              استخدام الحالة التلقائية
            </button>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
