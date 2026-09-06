"use client";

import { ChevronDown, ExternalLink } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import type { GeneratedQuestion, QuestionGenerationPriority } from "../../types/question";

const PRIORITY_LABELS: Record<QuestionGenerationPriority, string> = {
  high: "أولوية عالية",
  medium: "أولوية متوسطة",
  low: "أولوية منخفضة",
};

const PRIORITY_STYLES: Record<QuestionGenerationPriority, string> = {
  high: "bg-blue-50 text-blue-700",
  medium: "bg-secondary text-[#5F6368]",
  low: "bg-secondary/60 text-muted-foreground",
};

type GeneratedQuestionItemProps = {
  question: GeneratedQuestion;
  selected: boolean;
  onToggle: () => void;
};

export function GeneratedQuestionItem({ question, selected, onToggle }: GeneratedQuestionItemProps) {
  const [sourcesOpen, setSourcesOpen] = useState(false);

  return (
    <div
      className={cn(
        "rounded-lg border p-3 transition-colors",
        selected ? "border-[#1B8FEA]/40 bg-[#F7F8FA]" : "border-[#E6EAF0]",
      )}
    >
      <div className="flex items-start gap-3">
        <Checkbox
          checked={selected}
          onCheckedChange={onToggle}
          className="mt-0.5"
          aria-label="اختيار هذا السؤال"
        />
        <div className="min-w-0 flex-1 space-y-2">
          <p className="text-sm font-medium text-[#161616]">{question.text}</p>

          <div className="flex flex-wrap items-center gap-2">
            <Badge className={cn("border-0 font-normal", PRIORITY_STYLES[question.priority])}>
              {PRIORITY_LABELS[question.priority]}
            </Badge>
            <Badge variant="secondary" className="font-normal">
              {question.category}
            </Badge>
            {question.topic ? (
              <span className="text-xs text-[#5F6368]">الموضوع: {question.topic}</span>
            ) : null}
          </div>

          {question.reason ? (
            <p className="text-xs text-muted-foreground">{question.reason}</p>
          ) : null}

          {question.follow_up_questions.length > 0 ? (
            <div className="space-y-1 rounded-md bg-white/60 p-2">
              <p className="text-xs font-medium text-[#5F6368]">أسئلة متابعة مقترحة</p>
              <ul className="list-inside list-disc space-y-0.5">
                {question.follow_up_questions.map((followUp) => (
                  <li key={followUp} className="text-xs text-[#5F6368]">
                    {followUp}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {question.source_urls.length > 0 ? (
            <div>
              <button
                type="button"
                onClick={() => setSourcesOpen((value) => !value)}
                className="flex items-center gap-1 text-xs font-medium text-[#1B8FEA]"
              >
                المصادر ({question.source_urls.length})
                <ChevronDown
                  className={cn("size-3 transition-transform", sourcesOpen && "rotate-180")}
                  aria-hidden="true"
                />
              </button>
              {sourcesOpen ? (
                <div className="mt-1 flex flex-wrap gap-2">
                  {question.source_urls.map((url) => (
                    <a
                      key={url}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-[#1B8FEA] hover:underline"
                    >
                      <ExternalLink className="size-3" aria-hidden="true" />
                      مصدر
                    </a>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
