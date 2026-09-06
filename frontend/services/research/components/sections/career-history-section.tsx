import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfidenceNote, SourceLinksRow } from "../item-meta";
import type { CareerHistoryItem } from "../../types/research";

export function CareerHistorySection({ items }: { items: CareerHistoryItem[] }) {
  if (!items || items.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>المسيرة المهنية</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.map((item, index) => {
          const heading = [item.role, item.company].filter(Boolean).join(" · ");
          const period = [item.start_date, item.end_date].filter(Boolean).join(" — ");

          return (
            <div
              key={index}
              className="rounded-lg border border-[#E6EAF0] p-3 last:mb-0"
            >
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                {heading ? (
                  <p className="text-sm font-medium text-[#161616]">{heading}</p>
                ) : null}
                {period ? <p className="text-xs text-[#5F6368]">{period}</p> : null}
              </div>
              {item.description ? (
                <p className="mt-1 text-sm text-[#5F6368]">{item.description}</p>
              ) : null}
              <ConfidenceNote confidence={item.confidence} />
              <SourceLinksRow urls={item.source_urls} />
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
