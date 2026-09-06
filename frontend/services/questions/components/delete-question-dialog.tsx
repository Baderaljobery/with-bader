"use client";

import { toast } from "sonner";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { ApiError } from "@/lib/api/client";
import { useDeleteQuestion } from "../hooks/use-question-mutations";
import type { Question } from "../types/question";

type DeleteQuestionDialogProps = {
  guestId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  question: Question;
};

export function DeleteQuestionDialog({ guestId, open, onOpenChange, question }: DeleteQuestionDialogProps) {
  const deleteQuestion = useDeleteQuestion(guestId);

  async function handleDelete() {
    try {
      await deleteQuestion.mutateAsync(question.id);
      toast.success("تم حذف السؤال");
      onOpenChange(false);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "حدث خطأ ما.";
      toast.error(message);
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>حذف هذا السؤال؟</AlertDialogTitle>
          <AlertDialogDescription>
            سيتم حذف السؤال نهائيًا. لا يمكن التراجع عن هذا الإجراء.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>إلغاء</AlertDialogCancel>
          <AlertDialogAction
            variant="destructive"
            disabled={deleteQuestion.isPending}
            onClick={handleDelete}
          >
            {deleteQuestion.isPending ? "جارٍ الحذف..." : "حذف السؤال"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
