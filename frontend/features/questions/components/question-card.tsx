"use client";

import { History, MoreVertical, Pencil, Sparkles, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DeleteQuestionDialog } from "./delete-question-dialog";
import { QuestionFormDialog } from "./question-form-dialog";
import { QuestionSourceBadge } from "./question-source-badge";
import { QuestionStatusBadge } from "./question-status-badge";
import type { Question } from "../types/question";

type QuestionCardProps = {
  guestId: string;
  question: Question;
  index: number;
  onImprove: (question: Question) => void;
  onShowHistory: (question: Question) => void;
};

export function QuestionCard({ guestId, question, index, onImprove, onShowHistory }: QuestionCardProps) {
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  return (
    <>
      <Card className="transition-shadow hover:shadow-[var(--shadow-elevated)]">
        <CardContent className="flex items-start gap-3">
          <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-secondary text-xs font-semibold text-[#1B8FEA]">
            {index + 1}
          </span>

          <div className="min-w-0 flex-1 space-y-2">
            <p className="text-sm font-medium text-[#161616]">{question.text}</p>
            <div className="flex flex-wrap items-center gap-2">
              <QuestionSourceBadge source={question.source} />
              <QuestionStatusBadge status={question.status} />
              {question.topic ? (
                <span className="text-xs text-[#5F6368]">الموضوع: {question.topic}</span>
              ) : null}
            </div>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger
              render={
                <Button variant="ghost" size="icon-sm" aria-label="إجراءات السؤال" />
              }
            >
              <MoreVertical className="size-4" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setEditOpen(true)}>
                <Pencil className="size-4" />
                تعديل
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onImprove(question)}>
                <Sparkles className="size-4" />
                تحسين بالذكاء الاصطناعي
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onShowHistory(question)}>
                <History className="size-4" />
                سجل النسخ
              </DropdownMenuItem>
              <DropdownMenuItem variant="destructive" onClick={() => setDeleteOpen(true)}>
                <Trash2 className="size-4" />
                حذف
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </CardContent>
      </Card>

      <QuestionFormDialog guestId={guestId} open={editOpen} onOpenChange={setEditOpen} question={question} />
      <DeleteQuestionDialog guestId={guestId} open={deleteOpen} onOpenChange={setDeleteOpen} question={question} />
    </>
  );
}
