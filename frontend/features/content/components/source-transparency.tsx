import { Badge } from "@/components/ui/badge";
import { SOURCE_LABELS } from "../lib/labels";
import type { ContentSourceCategory } from "../types/content";

type SourceTransparencyProps = {
  sources: ContentSourceCategory[];
};

/** Subtle "based on" transparency - category labels only (المقابلة/الدفتر/
 * البحث/...), never the raw prompt or model response. */
export function SourceTransparency({ sources }: SourceTransparencyProps) {
  if (sources.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="text-xs text-muted-foreground">تم الاعتماد على:</span>
      {sources.map((source) => (
        <Badge key={source} variant="secondary" className="font-normal">
          {SOURCE_LABELS[source]}
        </Badge>
      ))}
    </div>
  );
}
