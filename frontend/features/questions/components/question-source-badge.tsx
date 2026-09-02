import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { QuestionSource } from "../types/question";

const SOURCE_LABELS: Record<QuestionSource, string> = {
  manual: "يدوي",
  ai_generated: "مولد بالذكاء الاصطناعي",
  ai_improved: "محسن بالذكاء الاصطناعي",
};

const SOURCE_STYLES: Record<QuestionSource, string> = {
  manual: "bg-secondary text-[#5F6368]",
  ai_generated: "bg-blue-50 text-blue-700",
  ai_improved: "bg-emerald-50 text-emerald-700",
};

export function QuestionSourceBadge({ source }: { source: QuestionSource }) {
  return (
    <Badge className={cn("border-0 font-normal", SOURCE_STYLES[source])}>
      {SOURCE_LABELS[source]}
    </Badge>
  );
}
