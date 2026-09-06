import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfidenceNote, SourceLinksRow } from "../item-meta";
import type { InterestingEventItem } from "../../types/research";

export function InterestingEventsSection({ items }: { items: InterestingEventItem[] }) {
  if (!items || items.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>أحداث ومحطات مهمة</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.map((item, index) => (
          <div key={index} className="rounded-lg border border-[#E6EAF0] p-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="text-sm font-medium text-[#161616]">{item.title}</p>
              {item.date ? <p className="text-xs text-[#5F6368]">{item.date}</p> : null}
            </div>
            {item.description ? (
              <p className="mt-1 text-sm text-[#5F6368]">{item.description}</p>
            ) : null}
            {item.why_interesting ? (
              <p className="mt-1 text-sm text-[#1B8FEA]">{item.why_interesting}</p>
            ) : null}
            <ConfidenceNote confidence={item.confidence} />
            <SourceLinksRow urls={item.source_urls} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
