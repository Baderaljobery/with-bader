import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { AnswerStatus } from "@/features/questions/types/question";

const STATUS_LABELS: Record<AnswerStatus, string> = {
  answered: "تمت الإجابة",
  not_answered: "بدون إجابة",
  uncertain: "تحتاج مراجعة",
};

const STATUS_STYLES: Record<AnswerStatus, string> = {
  answered: "bg-emerald-50 text-emerald-700",
  not_answered: "bg-secondary text-muted-foreground",
  uncertain: "bg-amber-50 text-amber-700",
};

export function AnswerStatusBadge({ status }: { status: AnswerStatus }) {
  return (
    <Badge className={cn("border-0 font-normal", STATUS_STYLES[status])}>
      {STATUS_LABELS[status]}
    </Badge>
  );
}
