import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { SourceLinksRow } from "../item-meta";
import type { InterviewAngleItem, InterviewAnglePriority } from "../../types/research";

const PRIORITY_LABELS: Record<InterviewAnglePriority, string> = {
  high: "أولوية عالية",
  medium: "أولوية متوسطة",
  low: "أولوية منخفضة",
};

// Deliberately calm, non-alarming palette - no red/orange "urgency" tones.
const PRIORITY_STYLES: Record<InterviewAnglePriority, string> = {
  high: "bg-blue-50 text-blue-700",
  medium: "bg-secondary text-[#5F6368]",
  low: "bg-secondary/60 text-muted-foreground",
};

export function InterviewAnglesSection({ items }: { items: InterviewAngleItem[] }) {
  if (!items || items.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>محاور مقترحة للمقابلة</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.map((item, index) => {
          const priority = item.priority ?? "medium";

          return (
            <div key={index} className="rounded-lg border border-[#E6EAF0] p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-medium text-[#161616]">{item.title}</p>
                <Badge className={cn("border-0 font-normal", PRIORITY_STYLES[priority])}>
                  {PRIORITY_LABELS[priority]}
                </Badge>
              </div>
              <p className="mt-1 text-sm text-[#5F6368]">{item.reason}</p>
              <SourceLinksRow urls={item.source_urls} />
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
