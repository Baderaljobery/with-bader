"use client";

import { Loader2 } from "lucide-react";
import { useEffect, useRef } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ApiError } from "@/lib/api/client";
import { useAcceptImprovement } from "../../hooks/use-accept-improvement";
import { useImproveQuestion } from "../../hooks/use-improve-question";
import type { Question } from "../../types/question";

type ImproveQuestionDialogProps = {
  guestId: string;
  question: Question | null;
  onOpenChange: (open: boolean) => void;
};

export function ImproveQuestionDialog({ guestId, question, onOpenChange }: ImproveQuestionDialogProps) {
  const improveQuestion = useImproveQuestion();
  const acceptImprovement = useAcceptImprovement(guestId);
  const startedForId = useRef<string | null>(null);

  useEffect(() => {
    if (!question) {
      startedForId.current = null;
      return;
    }
    if (startedForId.current === question.id) return;
    startedForId.current = question.id;

    improveQuestion.mutate(
      { questionId: question.id },
      {
        onError: () => {
          toast.error("تعذر تحسين السؤال، حاول مرة أخرى");
          onOpenChange(false);
        },
      },
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [question?.id]);

  function handleOpenChange(nextOpen: boolean) {
    if (!nextOpen) {
      improveQuestion.reset();
      startedForId.current = null;
    }
    onOpenChange(nextOpen);
  }

  async function handleAccept() {
    if (!question || !improveQuestion.data) return;
    try {
      await acceptImprovement.mutateAsync({
        questionId: question.id,
        improvedText: improveQuestion.data.improved_text,
      });
      toast.success("تم اعتماد التحسين بنجاح");
      handleOpenChange(false);
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        toast.error("لم يتغير نص السؤال بعد التحسين");
      } else {
        const message = error instanceof ApiError ? error.message : "تعذر اعتماد التحسين، حاول مرة أخرى";
        toast.error(message);
      }
    }
  }

  const preview = improveQuestion.data;

  return (
    <Dialog open={Boolean(question)} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-lg">
        {improveQuestion.isPending || !preview ? (
          <div className="flex flex-col items-center gap-4 py-6 text-center">
            <div className="flex size-14 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white shadow-sm">
              <Loader2 className="size-7 animate-spin" aria-hidden="true" />
            </div>
            <p className="font-heading text-base font-medium text-foreground">
              جارٍ تحسين السؤال بالذكاء الاصطناعي...
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <DialogHeader>
              <DialogTitle>تحسين السؤال بالذكاء الاصطناعي</DialogTitle>
              <DialogDescription>راجع الفرق بين النسخة الحالية والنسخة المحسنة قبل الاعتماد.</DialogDescription>
            </DialogHeader>

            <div className="space-y-3">
              <div className="rounded-lg border border-[#E6EAF0] p-3">
                <p className="mb-1 text-xs font-medium text-[#5F6368]">السؤال الحالي</p>
                <p className="text-sm text-[#161616]">{preview.original_text}</p>
              </div>
              <div className="rounded-lg border border-[#1B8FEA]/30 bg-[#F7F8FA] p-3">
                <p className="mb-1 text-xs font-medium text-[#1B8FEA]">النسخة المحسنة</p>
                <p className="text-sm text-[#161616]">{preview.improved_text}</p>
              </div>

              {preview.reason ? (
                <p className="text-xs text-muted-foreground">{preview.reason}</p>
              ) : null}

              {preview.changes.length > 0 ? (
                <ul className="list-inside list-disc space-y-0.5">
                  {preview.changes.map((change) => (
                    <li key={change} className="text-xs text-muted-foreground">
                      {change}
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => handleOpenChange(false)}>
                إلغاء
              </Button>
              <Button onClick={handleAccept} disabled={acceptImprovement.isPending}>
                {acceptImprovement.isPending ? "جارٍ الاعتماد..." : "اعتماد التحسين"}
              </Button>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
