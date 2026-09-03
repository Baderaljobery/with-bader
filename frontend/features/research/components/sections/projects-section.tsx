import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfidenceNote, SourceLinksRow } from "../item-meta";
import type { ProjectItem } from "../../types/research";

export function ProjectsSection({ items }: { items: ProjectItem[] }) {
  if (!items || items.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>المشاريع</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {items.map((item, index) => (
          <div key={index} className="rounded-lg border border-[#E6EAF0] p-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="text-sm font-medium text-[#161616]">{item.title}</p>
              {item.role ? <p className="text-xs text-[#5F6368]">{item.role}</p> : null}
            </div>
            {item.description ? (
              <p className="mt-1 text-sm text-[#5F6368]">{item.description}</p>
            ) : null}
            <ConfidenceNote confidence={item.confidence} />
            <SourceLinksRow urls={item.source_urls} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
