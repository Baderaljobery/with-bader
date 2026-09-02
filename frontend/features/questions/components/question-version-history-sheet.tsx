"use client";

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate } from "@/lib/format-date";
import { useQuestionVersions } from "../hooks/use-question-versions";
import { QuestionSourceBadge } from "./question-source-badge";
import type { Question } from "../types/question";

type QuestionVersionHistorySheetProps = {
  question: Question | null;
  onOpenChange: (open: boolean) => void;
};

export function QuestionVersionHistorySheet({ question, onOpenChange }: QuestionVersionHistorySheetProps) {
  const versions = useQuestionVersions(question?.id ?? null);

  return (
    <Sheet open={Boolean(question)} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-full px-4 sm:max-w-md">
        <SheetHeader>
          <SheetTitle>سجل النسخ</SheetTitle>
          <SheetDescription>
            سجل قراءة فقط لكل نسخ هذا السؤال، من الأحدث إلى الأقدم.
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 space-y-3 overflow-y-auto px-4 pb-4">
          {versions.isPending ? (
            <>
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-20 w-full" />
            </>
          ) : versions.isError ? (
            <p className="text-sm text-muted-foreground">تعذر تحميل سجل النسخ.</p>
          ) : versions.data.length === 0 ? (
            <p className="text-sm text-muted-foreground">لا توجد نسخ سابقة لهذا السؤال.</p>
          ) : (
            [...versions.data]
              .sort((a, b) => b.version - a.version)
              .map((version) => (
                <div key={version.id} className="rounded-lg border border-[#E6EAF0] p-3">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-[#161616]">
                        الإصدار {version.version}
                      </span>
                      <QuestionSourceBadge source={version.source} />
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(version.created_at)}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-[#161616]">{version.text}</p>
                </div>
              ))
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
