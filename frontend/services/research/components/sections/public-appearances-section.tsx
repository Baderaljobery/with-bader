import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfidenceNote, SourceLinksRow } from "../item-meta";
import type { PublicAppearanceItem } from "../../types/research";

/** Prior public activity - interviews, podcasts, panels, keynotes, articles
 * quoting the guest - all from BEFORE this research run. Never about the
 * upcoming With Bader interview itself. */
export function PublicAppearancesSection({ items }: { items: PublicAppearanceItem[] }) {
  if (!items || items.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>ظهور إعلامي سابق</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.map((item, index) => (
          <div key={index} className="rounded-lg border border-[#E6EAF0] p-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="text-sm font-medium text-[#161616]">{item.title}</p>
              {item.date ? <p className="text-xs text-[#5F6368]">{item.date}</p> : null}
            </div>
            {item.appearance_type || item.venue ? (
              <p className="mt-0.5 text-xs text-[#5F6368]">
                {[item.appearance_type, item.venue].filter(Boolean).join(" · ")}
              </p>
            ) : null}
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
