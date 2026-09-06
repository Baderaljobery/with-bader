import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { QuestionStatus } from "../types/question";

const STATUS_LABELS: Record<QuestionStatus, string> = {
  draft: "مسودة",
  approved: "معتمد",
  asked: "تم طرحه",
  answered: "تمت الإجابة",
};

const STATUS_STYLES: Record<QuestionStatus, string> = {
  draft: "bg-secondary text-muted-foreground",
  approved: "bg-violet-50 text-violet-700",
  asked: "bg-amber-50 text-amber-700",
  answered: "bg-emerald-50 text-emerald-700",
};

export function QuestionStatusBadge({ status }: { status: QuestionStatus }) {
  return (
    <Badge className={cn("border-0 font-normal", STATUS_STYLES[status])}>
      {STATUS_LABELS[status]}
    </Badge>
  );
}
