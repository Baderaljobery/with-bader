"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api/client";
import type { Question } from "@/features/questions/types/question";
import { useUpdateQuestionAnswer } from "../hooks/use-update-question-answer";
import type { QuestionAnswerState } from "../types/interview";
import { AnswerSourceBadge } from "./answer-source-badge";
import { AnswerStatusBadge } from "./answer-status-badge";

type QuestionAnswerCardProps = {
  guestId: string;
  question: Question;
  matchResult?: QuestionAnswerState;
  index: number;
};

export function QuestionAnswerCard({ guestId, question, matchResult, index }: QuestionAnswerCardProps) {
  const updateAnswer = useUpdateQuestionAnswer(guestId);
  const [draft, setDraft] = useState(question.answer ?? "");

  const isManual = question.answer_source === "manual";

  // Uncertain candidates only ever come from the immediate match response
  // (never persisted) - if the page was refreshed, matchResult is gone and
  // this stays hidden, which is correct: nothing was invented here.
  const candidateAnswer =
    question.answer_status === "uncertain" &&
    matchResult?.answer_status === "uncertain" &&
    matchResult.answer &&
    matchResult.answer !== question.answer
      ? matchResult.answer
      : null;

  async function persistAnswer(answer: string | null, spokenQuestion?: string | null) {
    try {
      await updateAnswer.mutateAsync({
        questionId: question.id,
        input: { answer, spoken_question: spokenQuestion },
      });
      toast.success(answer ? "تم حفظ الإجابة" : "تم مسح الإجابة");
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "تعذر حفظ الإجابة، حاول مرة أخرى";
      toast.error(message);
    }
  }

  function handleSave() {
    void persistAnswer(draft.trim() || null);
  }

  function handleClear() {
    setDraft("");
    void persistAnswer(null);
  }

  function handleUseCandidate() {
    if (!candidateAnswer) return;
    setDraft(candidateAnswer);
    void persistAnswer(candidateAnswer, matchResult?.spoken_question ?? undefined);
  }

  const unchanged = draft.trim() === (question.answer ?? "").trim();

  return (
    <Card>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <p className="text-sm font-medium text-[#161616]">
            <span className="text-[#5F6368]">{index + 1}. </span>
            {question.text}
          </p>
          <div className="flex shrink-0 items-center gap-1.5">
            <AnswerStatusBadge status={question.answer_status} />
            <AnswerSourceBadge source={question.answer_source} />
          </div>
        </div>

        {question.spoken_question ? (
          <p className="text-xs text-[#5F6368]">
            <span className="font-medium text-[#161616]">كما طُرح في المقابلة: </span>
            {question.spoken_question}
          </p>
        ) : null}

        {candidateAnswer ? (
          <div className="space-y-2 rounded-lg border border-dashed border-amber-300 bg-amber-50 p-3">
            <p className="text-xs font-medium text-amber-800">إجابة محتملة</p>
            <p className="text-sm text-amber-900">{candidateAnswer}</p>
            <Button
              size="sm"
              variant="outline"
              onClick={handleUseCandidate}
              disabled={updateAnswer.isPending}
            >
              استخدام هذه الإجابة
            </Button>
          </div>
        ) : null}

        <div className="space-y-2">
          <Textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="لم يتم العثور على إجابة — يمكنك إضافتها يدويًا"
            rows={3}
            className="min-h-20"
          />
          {isManual ? (
            <p className="text-xs text-muted-foreground">
              إجابة يدوية · لن يتم استبدالها تلقائيًا عند إعادة المطابقة
            </p>
          ) : null}
          <div className="flex items-center gap-2">
            <Button size="sm" onClick={handleSave} disabled={unchanged || updateAnswer.isPending}>
              {updateAnswer.isPending ? "جارٍ الحفظ..." : "حفظ الإجابة"}
            </Button>
            {question.answer ? (
              <Button
                size="sm"
                variant="outline"
                onClick={handleClear}
                disabled={updateAnswer.isPending}
              >
                مسح الإجابة
              </Button>
            ) : null}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
