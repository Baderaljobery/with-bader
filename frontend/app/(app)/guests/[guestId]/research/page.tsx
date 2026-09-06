"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { ErrorState } from "@/components/shared/error-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuest } from "@/services/guests/hooks/use-guest";
import { ResearchContent } from "@/services/research/components/research-content";
import { ResearchEmptyState } from "@/services/research/components/research-empty-state";
import { ResearchHeader } from "@/services/research/components/research-header";
import { ResearchLoadingState } from "@/services/research/components/research-loading-state";
import { useGuestResearch } from "@/services/research/hooks/use-guest-research";
import { useLatestGuestResearch } from "@/services/research/hooks/use-latest-guest-research";
import { useRunGuestResearch } from "@/services/research/hooks/use-run-guest-research";
import type { GuestResearchRunResponse } from "@/services/research/types/research";
import { ApiError } from "@/lib/api/client";

export default function GuestResearchPage() {
  const { guestId } = useParams<{ guestId: string }>();
  const { data: guest } = useGuest(guestId);

  const latest = useLatestGuestResearch(guestId);
  const runResearch = useRunGuestResearch(guestId);

  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);
  const selectedVersion = useGuestResearch(selectedVersionId);

  const [runMeta, setRunMeta] = useState<GuestResearchRunResponse | null>(null);

  function handleRun() {
    runResearch.mutate(undefined, {
      onSuccess: (data) => {
        setRunMeta(data);
        setSelectedVersionId(null);
        toast.success("تم تحديث بحث الضيف بنجاح");
      },
      onError: () => {
        toast.error("تعذر إكمال البحث، حاول مرة أخرى");
      },
    });
  }

  if (runResearch.isPending) {
    return <ResearchLoadingState />;
  }

  if (latest.isPending) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (latest.isError) {
    if (latest.error instanceof ApiError && latest.error.status === 404) {
      return <ResearchEmptyState onStart={handleRun} isPending={runResearch.isPending} />;
    }

    return (
      <ErrorState
        title="تعذر تحميل بيانات البحث"
        description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
        onRetry={() => latest.refetch()}
      />
    );
  }

  if (selectedVersionId) {
    if (selectedVersion.isPending) {
      return <Skeleton className="h-64 w-full" />;
    }
    if (selectedVersion.isError) {
      return (
        <ErrorState
          title="تعذر تحميل هذا الإصدار"
          description="حاول مرة أخرى أو عد إلى أحدث نسخة."
          onRetry={() => selectedVersion.refetch()}
        />
      );
    }
  }

  const displayedResearch = selectedVersionId ? selectedVersion.data : latest.data;
  if (!displayedResearch) return null;

  return (
    <div className="space-y-6">
      <ResearchHeader
        guestId={guestId}
        research={displayedResearch}
        latestId={latest.data.id}
        isViewingHistory={Boolean(selectedVersionId)}
        onSelectVersion={setSelectedVersionId}
        onRerun={handleRun}
        isRerunning={runResearch.isPending}
        runMeta={runMeta}
      />
      <ResearchContent
        research={displayedResearch}
        guestJobTitle={guest?.job_title ?? null}
        guestCompany={guest?.company ?? null}
      />
    </div>
  );
}
