"use client";

import { Palette } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuestDesigns } from "../hooks/use-guest-designs";
import type { DesignDraft } from "../types/design";
import { DesignDraftCard } from "./design-draft-card";

type DesignDraftsListProps = {
  guestId: string;
  onOpen: (design: DesignDraft) => void;
  onCreate: () => void;
};

export function DesignDraftsList({ guestId, onOpen, onCreate }: DesignDraftsListProps) {
  const { data: designs, isPending, isError, refetch } = useGuestDesigns(guestId);

  if (isPending) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="تعذر تحميل التصاميم"
        description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
        onRetry={() => refetch()}
      />
    );
  }

  if (designs.length === 0) {
    return (
      <EmptyState
        icon={Palette}
        title="لم يتم إنشاء أي تصميم لهذا الضيف بعد"
        description="حوّل المحتوى المحفوظ أو إجابات المقابلة إلى تصميم بصري جاهز للمشاركة."
        action={<Button onClick={onCreate}>إنشاء تصميم</Button>}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {designs.map((design) => (
        <DesignDraftCard key={design.id} guestId={guestId} design={design} onOpen={onOpen} />
      ))}
    </div>
  );
}
