import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { PreparationStatus } from "../types/guest";

const PREPARATION_STATUS_LABELS: Record<PreparationStatus, string> = {
  not_started: "لم يبدأ",
  researching: "قيد البحث",
  questions_ready: "الأسئلة جاهزة",
  interview_scheduled: "المقابلة مجدولة",
  interview_completed: "المقابلة مكتملة",
};

const PREPARATION_STATUS_STYLES: Record<PreparationStatus, string> = {
  not_started: "bg-secondary text-muted-foreground",
  researching: "bg-amber-50 text-amber-700",
  questions_ready: "bg-blue-50 text-blue-700",
  interview_scheduled: "bg-violet-50 text-violet-700",
  interview_completed: "bg-emerald-50 text-emerald-700",
};

export function GuestStatusBadge({ status }: { status: PreparationStatus }) {
  return (
    <Badge className={cn("border-0 font-normal", PREPARATION_STATUS_STYLES[status])}>
      {PREPARATION_STATUS_LABELS[status]}
    </Badge>
  );
}
