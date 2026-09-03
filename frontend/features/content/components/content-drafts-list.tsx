"use client";

import { FileEdit } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuestContent } from "../hooks/use-guest-content";
import type { ContentDraft } from "../types/content";
import { ContentDraftCard } from "./content-draft-card";

type ContentDraftsListProps = {
  guestId: string;
  onOpen: (draft: ContentDraft) => void;
  onCreate: () => void;
};

export function ContentDraftsList({ guestId, onOpen, onCreate }: ContentDraftsListProps) {
  const { data: drafts, isPending, isError, refetch } = useGuestContent(guestId);

  if (isPending) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="تعذر تحميل المحتوى"
        description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
        onRetry={() => refetch()}
      />
    );
  }

  if (drafts.length === 0) {
    return (
      <EmptyState
        icon={FileEdit}
        title="لم يتم إنشاء محتوى لهذا الضيف بعد"
        description="حوّل البحث والمقابلة والملاحظات إلى محتوى جاهز للمراجعة."
        action={<Button onClick={onCreate}>إنشاء محتوى</Button>}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {drafts.map((draft) => (
        <ContentDraftCard key={draft.id} guestId={guestId} draft={draft} onOpen={onOpen} />
      ))}
    </div>
  );
}
