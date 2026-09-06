import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfidenceNote, SourceLinksRow } from "../item-meta";
import type { EducationItem } from "../../types/research";

export function EducationSection({ items }: { items: EducationItem[] }) {
  if (!items || items.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>التعليم</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.map((item, index) => {
          const heading = [item.degree, item.field].filter(Boolean).join(" · ");

          return (
            <div key={index} className="rounded-lg border border-[#E6EAF0] p-3">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                {item.institution ? (
                  <p className="text-sm font-medium text-[#161616]">{item.institution}</p>
                ) : null}
                {item.year ? <p className="text-xs text-[#5F6368]">{item.year}</p> : null}
              </div>
              {heading ? <p className="mt-1 text-sm text-[#5F6368]">{heading}</p> : null}
              <ConfidenceNote confidence={item.confidence} />
              <SourceLinksRow urls={item.source_urls} />
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
