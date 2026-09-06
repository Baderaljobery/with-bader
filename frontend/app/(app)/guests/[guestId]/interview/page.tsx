"use client";

import { useParams } from "next/navigation";
import { useState } from "react";

import { SectionHeader } from "@/components/shared/section-header";
import { ErrorState } from "@/components/shared/error-state";
import { Skeleton } from "@/components/ui/skeleton";
import { InterviewEmptyState } from "@/services/interview/components/interview-empty-state";
import { InterviewLoadingState } from "@/services/interview/components/interview-loading-state";
import { InterviewUploadDialog } from "@/services/interview/components/interview-upload-dialog";
import { QuestionsAnswersSection } from "@/services/interview/components/questions-answers-section";
import { TranscriptCard } from "@/services/interview/components/transcript-card";
import { useGuestTranscript } from "@/services/interview/hooks/use-guest-transcript";
import { useMatchGuestAnswers } from "@/services/interview/hooks/use-match-answers";
import { mapMatchingError } from "@/services/interview/lib/error-messages";
import type { QuestionAnswerState } from "@/services/interview/types/interview";
import { ApiError } from "@/lib/api/client";
import { toast } from "sonner";

export default function GuestInterviewPage() {
  const { guestId } = useParams<{ guestId: string }>();

  const transcript = useGuestTranscript(guestId);
  const matchAnswers = useMatchGuestAnswers(guestId);

  const [uploadOpen, setUploadOpen] = useState(false);
  const [lastMatchResult, setLastMatchResult] = useState<QuestionAnswerState[] | null>(null);

  function handleRematch() {
    matchAnswers.mutate(undefined, {
      onSuccess: (data) => {
        setLastMatchResult(data.questions);
        toast.success("تمت إعادة مطابقة الإجابات بنجاح");
      },
      onError: (error) => {
        toast.error(mapMatchingError(error));
      },
    });
  }

  return (
    <div className="space-y-6">
      <SectionHeader
        title="المقابلة"
        description="تفريغ نص المقابلة وربط الإجابات المستخرجة بالأسئلة المحفوظة"
      />

      {matchAnswers.isPending ? (
        <InterviewLoadingState mode="matching" />
      ) : transcript.isPending ? (
        <div className="space-y-4">
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      ) : transcript.isError ? (
        transcript.error instanceof ApiError && transcript.error.status === 404 ? (
          <InterviewEmptyState onUpload={() => setUploadOpen(true)} />
        ) : (
          <ErrorState
            title="تعذر تحميل المقابلة"
            description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
            onRetry={() => transcript.refetch()}
          />
        )
      ) : (
        <>
          <TranscriptCard
            guestId={guestId}
            transcript={transcript.data}
            onRematch={handleRematch}
            isRematching={matchAnswers.isPending}
            onReplace={() => setUploadOpen(true)}
          />

          <div className="space-y-3">
            <h2 className="font-heading text-base font-semibold text-[#161616]">الأسئلة والإجابات</h2>
            <QuestionsAnswersSection guestId={guestId} lastMatchResult={lastMatchResult} />
          </div>
        </>
      )}

      <InterviewUploadDialog
        guestId={guestId}
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        hasExistingTranscript={Boolean(transcript.data)}
        onTranscribed={(data) => setLastMatchResult(data.questions)}
      />
    </div>
  );
}
