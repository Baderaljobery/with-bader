"use client";

import { ListChecks } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuestQuestions } from "../hooks/use-guest-questions";
import { QuestionCard } from "./question-card";
import type { Question } from "../types/question";

function QuestionListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 3 }).map((_, index) => (
        <Card key={index}>
          <CardContent className="flex items-start gap-3">
            <Skeleton className="size-6 shrink-0 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/3" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

type QuestionListProps = {
  guestId: string;
  onAddManual: () => void;
  onGenerate: () => void;
  onImprove: (question: Question) => void;
  onShowHistory: (question: Question) => void;
};

export function QuestionList({ guestId, onAddManual, onGenerate, onImprove, onShowHistory }: QuestionListProps) {
  const { data: questions, isPending, isError, refetch } = useGuestQuestions(guestId);

  if (isPending) {
    return <QuestionListSkeleton />;
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
        title="لا توجد أسئلة لهذا الضيف بعد"
        description="أضف سؤالًا يدويًا أو أنشئ مجموعة أسئلة مخصصة باستخدام الذكاء الاصطناعي."
        action={
          <div className="flex flex-wrap items-center justify-center gap-2">
            <Button variant="outline" onClick={onAddManual}>
              إضافة سؤال
            </Button>
            <Button onClick={onGenerate}>إنشاء أسئلة بالذكاء الاصطناعي</Button>
          </div>
        }
      />
    );
  }

  return (
    <div className="space-y-3">
      {questions.map((question, index) => (
        <QuestionCard
          key={question.id}
          guestId={guestId}
          question={question}
          index={index}
          onImprove={onImprove}
          onShowHistory={onShowHistory}
        />
      ))}
    </div>
  );
}
