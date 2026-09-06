"use client";

import { ArrowRight, UserX } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import type { ReactNode } from "react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api/client";
import { useGuest } from "../hooks/use-guest";
import { GuestWorkspaceHeader } from "./guest-workspace-header";
import { GuestWorkspaceTabs } from "./guest-workspace-tabs";

function BackToGuestsLink() {
  return (
    <Link
      href="/"
      className="inline-flex items-center gap-1.5 text-sm font-medium text-[#5F6368] transition-colors hover:text-[#161616]"
    >
      <ArrowRight className="size-4" aria-hidden="true" />
      العودة إلى الضيوف
    </Link>
  );
}

export function GuestWorkspaceShell({ children }: { children: ReactNode }) {
  const { guestId } = useParams<{ guestId: string }>();
  const { data: guest, isPending, isError, error, refetch } = useGuest(guestId);

  if (isPending) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-28" />
        <div className="flex items-center gap-4">
          <Skeleton className="size-14 shrink-0 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-3.5 w-32" />
          </div>
        </div>
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (isError) {
    if (error instanceof ApiError && error.status === 404) {
      return (
        <div className="space-y-6">
          <BackToGuestsLink />
          <EmptyState
            icon={UserX}
            title="تعذر العثور على الضيف"
            description="ربما تم حذف هذا الضيف، أو أن الرابط غير صحيح."
          />
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <BackToGuestsLink />
        <ErrorState
          title="تعذر تحميل بيانات الضيف"
          description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <BackToGuestsLink />
      <GuestWorkspaceHeader guest={guest} />
      <GuestWorkspaceTabs guestId={guestId} />
      {children}
    </div>
  );
}
