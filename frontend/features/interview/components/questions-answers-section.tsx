"use client";

import { ListChecks } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuestQuestions } from "@/features/questions/hooks/use-guest-questions";
import { QuestionAnswerCard } from "./question-answer-card";
import type { QuestionAnswerState } from "../types/interview";

type QuestionsAnswersSectionProps = {
  guestId: string;
  lastMatchResult: QuestionAnswerState[] | null;
};

export function QuestionsAnswersSection({ guestId, lastMatchResult }: QuestionsAnswersSectionProps) {
  const { data: questions, isPending, isError, refetch } = useGuestQuestions(guestId);

  if (isPending) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="تعذر تحميل الأسئلة"
        description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
        onRetry={() => refetch()}
      />
    );
  }

  if (questions.length === 0) {
    return (
      <EmptyState
        icon={ListChecks}
        title="لا توجد أسئلة محفوظة لهذا الضيف"
        description="أضف أسئلة من تبويب الأسئلة أولًا حتى تتمكن من مطابقة الإجابات."
      />
    );
  }

  const matchByQuestionId = new Map(lastMatchResult?.map((item) => [item.question_id, item]));

  return (
    <div className="space-y-3">
      {questions.map((question, index) => (
        <QuestionAnswerCard
          key={`${question.id}-${question.answer_updated_at ?? "none"}`}
          guestId={guestId}
          question={question}
          matchResult={matchByQuestionId.get(question.id)}
          index={index}
        />
      ))}
    </div>
  );
}
