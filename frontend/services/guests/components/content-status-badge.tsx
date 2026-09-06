import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { CONTENT_STATUS_LABELS } from "../lib/content-status-labels";
import type { ContentStatus } from "../types/guest";

// Subtle badge-style tones only - no saturated traffic-light colors. Kept
// in sync with content-status-select.tsx's trigger colors.
const CONTENT_STATUS_BADGE_STYLES: Record<ContentStatus, string> = {
  not_started: "bg-secondary text-muted-foreground",
  in_progress: "bg-[#1B8FEA]/10 text-[#1B8FEA]",
  published: "bg-emerald-50 text-emerald-700",
};

/** Read-only content-status badge for the guest list card - the same
 * guest.content_status the Guest Overview's ContentStatusSelect shows, so
 * the two never disagree (see content-status-select.tsx). */
export function ContentStatusBadge({ status }: { status: ContentStatus }) {
  return (
    <Badge className={cn("border-0 font-normal", CONTENT_STATUS_BADGE_STYLES[status])}>
      {CONTENT_STATUS_LABELS[status]}
    </Badge>
  );
}
