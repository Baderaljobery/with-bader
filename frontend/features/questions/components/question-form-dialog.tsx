"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError } from "@/lib/api/client";
import { useCreateQuestion, useUpdateQuestion } from "../hooks/use-question-mutations";
import { useGuestQuestions } from "../hooks/use-guest-questions";
import {
  questionFormSchema,
  questionFormValuesToInput,
  type QuestionFormValues,
} from "../schemas/question-schema";
import type { Question } from "../types/question";

type QuestionFormDialogProps = {
  guestId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  question?: Question;
};

function defaultValuesFor(question?: Question): QuestionFormValues {
  return {
    text: question?.text ?? "",
    topic: question?.topic ?? "",
  };
}

export function QuestionFormDialog({ guestId, open, onOpenChange, question }: QuestionFormDialogProps) {
  const isEdit = Boolean(question);
  const { data: questions } = useGuestQuestions(guestId);
  const createQuestion = useCreateQuestion(guestId);
  const updateQuestion = useUpdateQuestion(guestId);
  const isSaving = isEdit ? updateQuestion.isPending : createQuestion.isPending;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<QuestionFormValues>({
    resolver: zodResolver(questionFormSchema),
    defaultValues: defaultValuesFor(question),
  });

  useEffect(() => {
    if (open) {
      reset(defaultValuesFor(question));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, question]);

  const onSubmit = handleSubmit(async (values) => {
    try {
      if (isEdit && question) {
        await updateQuestion.mutateAsync({
          questionId: question.id,
          input: questionFormValuesToInput(values),
        });
        toast.success("تم تحديث السؤال");
      } else {
        const nextPosition = (questions ?? []).reduce(
          (max, item) => Math.max(max, item.position),
          -1,
        ) + 1;
        await createQuestion.mutateAsync({
          ...questionFormValuesToInput(values),
          position: nextPosition,
        });
        toast.success("تمت إضافة السؤال");
      }
      onOpenChange(false);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "حدث خطأ ما.";
      toast.error(message);
    }
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={onSubmit} className="space-y-4">
          <DialogHeader>
            <DialogTitle>{isEdit ? "تعديل السؤال" : "إضافة سؤال"}</DialogTitle>
            <DialogDescription>
              {isEdit ? "قم بتحديث نص السؤال أو موضوعه." : "أضف سؤالًا جديدًا لهذا الضيف."}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-1.5">
            <Label htmlFor="question-text">نص السؤال</Label>
            <Input id="question-text" autoFocus {...register("text")} />
            {errors.text ? (
              <p className="text-xs text-destructive">{errors.text.message}</p>
            ) : null}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="question-topic">الموضوع (اختياري)</Label>
            <Input id="question-topic" {...register("topic")} />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              إلغاء
            </Button>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? "جارٍ الحفظ..." : isEdit ? "حفظ التغييرات" : "إضافة سؤال"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
