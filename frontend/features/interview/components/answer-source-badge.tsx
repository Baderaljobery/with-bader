import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { AnswerSource } from "@/features/questions/types/question";

const SOURCE_LABELS: Record<AnswerSource, string> = {
  manual: "يدوي",
  ai_extracted: "مستخرج بالذكاء الاصطناعي",
};

const SOURCE_STYLES: Record<AnswerSource, string> = {
  manual: "bg-secondary text-[#5F6368]",
  ai_extracted: "bg-blue-50 text-blue-700",
};

export function AnswerSourceBadge({ source }: { source: AnswerSource | null }) {
  if (!source) return null;

  return (
    <Badge className={cn("border-0 font-normal", SOURCE_STYLES[source])}>
      {SOURCE_LABELS[source]}
    </Badge>
  );
}
