"use client";

import { Plus, Sparkles } from "lucide-react";
import { useParams } from "next/navigation";
import { useState } from "react";

import { SectionHeader } from "@/components/shared/section-header";
import { Button } from "@/components/ui/button";
import { GenerationDialog } from "@/services/questions/components/generation/generation-dialog";
import { GenerationPreviewSheet } from "@/services/questions/components/generation/generation-preview-sheet";
import { ImproveQuestionDialog } from "@/services/questions/components/improvement/improve-question-dialog";
import { QuestionFormDialog } from "@/services/questions/components/question-form-dialog";
import { QuestionList } from "@/services/questions/components/question-list";
import { QuestionVersionHistorySheet } from "@/services/questions/components/question-version-history-sheet";
import type { Question, QuestionGenerationResponse } from "@/services/questions/types/question";

export default function GuestQuestionsPage() {
  const { guestId } = useParams<{ guestId: string }>();

  const [addOpen, setAddOpen] = useState(false);
  const [generationOpen, setGenerationOpen] = useState(false);
  const [generationResult, setGenerationResult] = useState<QuestionGenerationResponse | null>(null);
  const [improvingQuestion, setImprovingQuestion] = useState<Question | null>(null);
  const [historyQuestion, setHistoryQuestion] = useState<Question | null>(null);

  return (
    <div className="space-y-6">
      <SectionHeader
        title="الأسئلة"
        description="إدارة أسئلة المقابلة وإنشاؤها وتحسينها بالذكاء الاصطناعي"
        action={
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="outline" onClick={() => setAddOpen(true)}>
              <Plus className="size-4" />
              إضافة سؤال
            </Button>
            <Button onClick={() => setGenerationOpen(true)}>
              <Sparkles className="size-4" />
              إنشاء أسئلة بالذكاء الاصطناعي
            </Button>
          </div>
        }
      />

      <QuestionList
        guestId={guestId}
        onAddManual={() => setAddOpen(true)}
        onGenerate={() => setGenerationOpen(true)}
        onImprove={setImprovingQuestion}
        onShowHistory={setHistoryQuestion}
      />

      <QuestionFormDialog guestId={guestId} open={addOpen} onOpenChange={setAddOpen} />

      <GenerationDialog
        guestId={guestId}
        open={generationOpen}
        onOpenChange={setGenerationOpen}
        onGenerated={setGenerationResult}
      />
      <GenerationPreviewSheet
        guestId={guestId}
        result={generationResult}
        onOpenChange={(open) => {
          if (!open) setGenerationResult(null);
        }}
      />

      <ImproveQuestionDialog
        guestId={guestId}
        question={improvingQuestion}
        onOpenChange={(open) => {
          if (!open) setImprovingQuestion(null);
        }}
      />

      <QuestionVersionHistorySheet
        question={historyQuestion}
        onOpenChange={(open) => {
          if (!open) setHistoryQuestion(null);
        }}
      />
    </div>
  );
}
