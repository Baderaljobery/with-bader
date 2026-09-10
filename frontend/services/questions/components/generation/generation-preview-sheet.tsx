"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { ApiError } from "@/lib/api/client";
import { useSaveGeneratedQuestions } from "../../hooks/use-save-generated-questions";
import type { QuestionGenerationResponse } from "../../types/question";
import { GeneratedQuestionItem } from "./generated-question-item";

type GenerationPreviewSheetProps = {
  guestId: string;
  result: QuestionGenerationResponse | null;
  onOpenChange: (open: boolean) => void;
};

export function GenerationPreviewSheet({ guestId, result, onOpenChange }: GenerationPreviewSheetProps) {
  const saveGenerated = useSaveGeneratedQuestions(guestId);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [selectedForResult, setSelectedForResult] = useState<QuestionGenerationResponse | null>(null);

  // Reset selection whenever a new generation result comes in, using React's
  // "adjust state during render" pattern instead of an effect - pre-selects
  // everything, but nothing is persisted until "حفظ الأسئلة المحددة" is
  // explicitly clicked.
  if (result !== selectedForResult) {
    setSelectedForResult(result);
    setSelected(result ? new Set(result.questions.map((_, index) => index)) : new Set());
  }

  function toggle(index: number) {
    setSelected((current) => {
      const next = new Set(current);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }

  function toggleAll() {
    if (!result) return;
    setSelected((current) =>
      current.size === result.questions.length
        ? new Set()
        : new Set(result.questions.map((_, index) => index)),
    );
  }

  async function handleSave() {
    if (!result) return;
    const selectedQuestions = result.questions.filter((_, index) => selected.has(index));
    if (selectedQuestions.length === 0) return;

    try {
      const response = await saveGenerated.mutateAsync({
        generation_run_id: result.generation_run_id,
        research_id: result.research_id,
        research_version: result.research_version,
        questions: selectedQuestions,
      });
      if (response.saved_count > 0) {
        toast.success(
          response.skipped_count > 0
            ? `تم حفظ ${response.saved_count} وتجاوز ${response.skipped_count} سؤال مكرر`
            : `تم حفظ ${response.saved_count} سؤال بنجاح`,
        );
      } else {
        toast.info("لم تُحفظ أسئلة جديدة لأن المحدد محفوظ مسبقًا");
      }
      onOpenChange(false);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "تعذر حفظ الأسئلة، حاول مرة أخرى";
      toast.error(message);
    }
  }

  const allSelected = Boolean(result) && selected.size === result?.questions.length;

  return (
    <Sheet open={Boolean(result)} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="flex w-full flex-col px-4 sm:max-w-lg">
        <SheetHeader>
          <SheetTitle>معاينة الأسئلة المقترحة</SheetTitle>
          <SheetDescription>
            راجع الأسئلة واختر ما تريد حفظه. لن يتم حفظ أي سؤال قبل ضغط زر الحفظ.
          </SheetDescription>
        </SheetHeader>

        {result ? (
          <>
            {result.generated_count < result.requested_count ? (
              <p className="mx-4 rounded-lg border border-[#E6EAF0] bg-[#F7F8FA] px-3 py-2 text-xs text-[#5F6368]">
                تم عرض {result.generated_count} من أصل {result.requested_count} بعد استبعاد الأسئلة
                المكررة أو المتشابهة.
              </p>
            ) : null}
            <div className="flex items-center justify-between px-4">
              <label className="flex items-center gap-2 text-sm text-[#5F6368]">
                <Checkbox checked={allSelected} onCheckedChange={toggleAll} />
                تحديد الكل ({result.questions.length})
              </label>
              <span className="text-xs text-muted-foreground">
                محدد: {selected.size} من {result.questions.length}
              </span>
            </div>

            <div className="flex-1 space-y-3 overflow-y-auto px-4 pb-4">
              {result.questions.map((question, index) => (
                <GeneratedQuestionItem
                  key={index}
                  question={question}
                  selected={selected.has(index)}
                  onToggle={() => toggle(index)}
                />
              ))}
            </div>

            <SheetFooter className="flex-row justify-end gap-2 border-t border-[#E6EAF0] pt-4">
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                إلغاء
              </Button>
              <Button onClick={handleSave} disabled={selected.size === 0 || saveGenerated.isPending}>
                {saveGenerated.isPending
                  ? "جارٍ الحفظ..."
                  : `حفظ الأسئلة المحددة (${selected.size})`}
              </Button>
            </SheetFooter>
          </>
        ) : null}
      </SheetContent>
    </Sheet>
  );
}
