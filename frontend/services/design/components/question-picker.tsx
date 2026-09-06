"use client";

import { useMemo } from "react";

import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuestQuestions } from "@/services/questions/hooks/use-guest-questions";

type QuestionPickerProps = {
  guestId: string;
  value: string[];
  onChange: (questionIds: string[]) => void;
  disabled?: boolean;
};

/** Only answered questions are selectable - an unanswered one is never
 * usable as design content (same grounding rule as the backend context
 * builders across this app). */
export function QuestionPicker({ guestId, value, onChange, disabled }: QuestionPickerProps) {
  const { data: questions, isPending } = useGuestQuestions(guestId);

  const answered = useMemo(
    () => (questions ?? []).filter((question) => question.answer_status === "answered" && question.answer),
    [questions],
  );

  if (isPending) {
    return <Skeleton className="h-16 w-full" />;
  }

  if (answered.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        لا توجد أسئلة مُجابة بعد لاستخدامها كمصدر داعم.
      </p>
    );
  }

  function toggle(questionId: string, checked: boolean) {
    onChange(checked ? [...value, questionId] : value.filter((id) => id !== questionId));
  }

  return (
    <div className="max-h-56 space-y-1 overflow-y-auto rounded-2xl border border-border p-2">
      {answered.map((question) => {
        const checked = value.includes(question.id);
        return (
          <label
            key={question.id}
            className="flex cursor-pointer items-start gap-2.5 rounded-xl px-2.5 py-2 text-sm hover:bg-secondary/60"
          >
            <Checkbox
              checked={checked}
              onCheckedChange={(next) => toggle(question.id, next === true)}
              disabled={disabled}
              className="mt-0.5"
            />
            <span className="space-y-0.5">
              <span className="block font-medium text-foreground">{question.text}</span>
              <span className="line-clamp-1 block text-xs text-muted-foreground">{question.answer}</span>
            </span>
          </label>
        );
      })}
    </div>
  );
}
