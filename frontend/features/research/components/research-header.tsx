import { RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/format-date";
import { ResearchVersionHistory } from "./research-version-history";
import type { GuestResearch, GuestResearchRunResponse } from "../types/research";

type ResearchHeaderProps = {
  guestId: string;
  research: GuestResearch;
  latestId: string;
  isViewingHistory: boolean;
  onSelectVersion: (researchId: string | null) => void;
  onRerun: () => void;
  isRerunning: boolean;
  runMeta: GuestResearchRunResponse | null;
};

export function ResearchHeader({
  guestId,
  research,
  latestId,
  isViewingHistory,
  onSelectVersion,
  onRerun,
  isRerunning,
  runMeta,
}: ResearchHeaderProps) {
  return (
    <div className="space-y-3">
      <div className="relative overflow-hidden rounded-2xl border border-border bg-white px-5 py-4 shadow-[var(--shadow-soft)]">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-12 end-[-2rem] size-44 rounded-full opacity-60 blur-2xl"
          style={{ backgroundImage: "var(--glow-blue)" }}
        />
        <div className="relative flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h2 className="font-heading text-lg font-semibold text-[#161616]">ملف البحث</h2>
              <Badge variant="secondary" className="font-normal">
                الإصدار {research.version}
              </Badge>
            </div>
            <p className="text-sm text-[#5F6368]">آخر تحديث: {formatDate(research.created_at)}</p>
          </div>

          <div className="flex items-center gap-2">
            <ResearchVersionHistory
              guestId={guestId}
              latestId={latestId}
              activeResearchId={research.id}
              onSelectVersion={onSelectVersion}
            />
            <Button size="sm" onClick={onRerun} disabled={isRerunning}>
              <RefreshCw className="size-4" />
              {isRerunning ? "جارٍ إعادة البحث..." : "إعادة البحث"}
            </Button>
          </div>
        </div>
      </div>

      {isViewingHistory ? (
        <div className="rounded-lg border border-[#E6EAF0] bg-[#F7F8FA] px-3 py-2 text-xs text-[#5F6368]">
          أنت تعرض نسخة سابقة من البحث (الإصدار {research.version}).{" "}
          <button
            type="button"
            onClick={() => onSelectVersion(null)}
            className="font-medium text-[#1B8FEA] hover:underline"
          >
            العودة إلى أحدث نسخة
          </button>
        </div>
      ) : null}

      {runMeta ? (
        <p className="text-xs text-muted-foreground">
          آخر تشغيل: {runMeta.search_provider}
          {runMeta.fallback_queries_used > 0 && runMeta.fallback_search_provider
            ? ` (احتياطي: ${runMeta.fallback_search_provider})`
            : ""}{" "}
          · {runMeta.extractor_provider}
        </p>
      ) : null}
    </div>
  );
}
