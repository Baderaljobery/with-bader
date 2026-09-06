"use client";

import { HelpCircle, Link2, Unlink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Textarea } from "@/components/ui/textarea";
import { useGuestQuestions } from "@/services/questions/hooks/use-guest-questions";
import { useLocalDraft } from "../../hooks/use-local-draft";
import { getBlockText } from "../../lib/block-content";
import type { Block } from "../../types/block";

type QuestionBlockProps = {
  block: Block;
  guestId: string;
  autoFocus?: boolean;
  textareaRef?: (element: HTMLTextAreaElement | null) => void;
  onSaveText: (text: string) => void;
  onLink: (questionId: string | null) => void;
  onEnter?: () => void;
  onBackspaceEmpty?: () => void;
};

export function QuestionBlock({
  block,
  guestId,
  autoFocus,
  textareaRef,
  onSaveText,
  onLink,
  onEnter,
  onBackspaceEmpty,
}: QuestionBlockProps) {
  const { value, handleChange, flush } = useLocalDraft(getBlockText(block.content), onSaveText);
  const { data: questions } = useGuestQuestions(guestId);

  // If the linked question was later deleted, the backend already sets
  // linked_question_id to null server-side (ON DELETE SET NULL) - this
  // lookup only has to handle "still loading" vs "found" for a currently
  // valid link, never a dangling id.
  const linkedQuestion = block.linked_question_id
    ? questions?.find((question) => question.id === block.linked_question_id)
    : null;

  return (
    <div className="space-y-1.5 rounded-lg border border-border bg-secondary/30 px-3 py-2">
      <div className="flex items-start gap-2">
        <HelpCircle className="mt-2 size-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
        <Textarea
          ref={textareaRef}
          autoFocus={autoFocus}
          value={value}
          placeholder="سؤال"
          onChange={(event) => handleChange(event.target.value)}
          onBlur={flush}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey && onEnter) {
              event.preventDefault();
              flush();
              onEnter();
            } else if (event.key === "Backspace" && value === "" && onBackspaceEmpty) {
              event.preventDefault();
              onBackspaceEmpty();
            }
          }}
          rows={1}
          className="min-h-0 resize-none border-none bg-transparent p-0 text-sm leading-7 text-foreground shadow-none focus-visible:ring-0"
        />
      </div>

      <div className="ps-6">
        {block.linked_question_id ? (
          <div className="flex flex-wrap items-center gap-1.5">
            <Badge
              variant="outline"
              className="max-w-full gap-1 border-0 bg-background font-normal text-muted-foreground"
            >
              <Link2 className="size-3 shrink-0" aria-hidden="true" />
              <span className="truncate">مرتبط بسؤال: {linkedQuestion ? linkedQuestion.text : "..."}</span>
            </Badge>
            <Button
              type="button"
              variant="ghost"
              size="xs"
              className="h-5 px-1.5 text-xs"
              onClick={() => onLink(null)}
            >
              <Unlink className="size-3" aria-hidden="true" />
              إلغاء الربط
            </Button>
          </div>
        ) : questions && questions.length > 0 ? (
          <DropdownMenu>
            <DropdownMenuTrigger
              render={
                <Button
                  type="button"
                  variant="ghost"
                  size="xs"
                  className="h-5 px-1.5 text-xs text-muted-foreground"
                />
              }
            >
              <Link2 className="size-3" aria-hidden="true" />
              ربط بسؤال محفوظ
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="max-w-72">
              {questions.map((question) => (
                <DropdownMenuItem
                  key={question.id}
                  onClick={() => onLink(question.id)}
                  className="whitespace-normal"
                >
                  {question.text}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        ) : null}
      </div>
    </div>
  );
}
