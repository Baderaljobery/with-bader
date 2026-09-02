"use client";

import type { LucideIcon } from "lucide-react";

import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useLocalDraft } from "../../hooks/use-local-draft";
import { getBlockText } from "../../lib/block-content";
import type { Block } from "../../types/block";

type TextBlockVariant = {
  wrapperClassName?: string;
  textClassName: string;
  placeholder: string;
};

const VARIANTS: Partial<Record<Block["type"], TextBlockVariant>> = {
  heading: {
    textClassName: "font-heading text-lg font-semibold text-foreground",
    placeholder: "عنوان بدون نص",
  },
  paragraph: {
    textClassName: "text-sm leading-7 text-foreground",
    placeholder: "اكتب هنا...",
  },
  answer: {
    textClassName: "text-sm leading-7 text-foreground",
    placeholder: "الإجابة...",
  },
  quote: {
    wrapperClassName: "border-e-2 border-border ps-3",
    textClassName: "text-sm leading-7 text-muted-foreground italic",
    placeholder: "اقتباس",
  },
  highlight: {
    wrapperClassName: "rounded-lg bg-amber-50 px-3 py-2",
    textClassName: "text-sm leading-7 text-amber-900",
    placeholder: "نص مميز",
  },
  callout: {
    wrapperClassName: "rounded-lg bg-sky-50 px-3 py-2",
    textClassName: "text-sm leading-7 text-sky-900",
    placeholder: "ملاحظة مهمة",
  },
  personal_note: {
    wrapperClassName: "rounded-lg bg-violet-50 px-3 py-2",
    textClassName: "text-sm leading-7 text-violet-900",
    placeholder: "ملاحظة شخصية",
  },
  content_idea: {
    wrapperClassName: "rounded-lg bg-emerald-50 px-3 py-2",
    textClassName: "text-sm leading-7 text-emerald-900",
    placeholder: "فكرة محتوى",
  },
  guest_info: {
    wrapperClassName: "rounded-lg bg-secondary px-3 py-2",
    textClassName: "text-sm leading-7 text-foreground",
    placeholder: "معلومات عن الضيف",
  },
};

const DEFAULT_VARIANT: TextBlockVariant = {
  textClassName: "text-sm leading-7 text-foreground",
  placeholder: "اكتب هنا...",
};

type TextBlockProps = {
  block: Block;
  icon: LucideIcon;
  autoFocus?: boolean;
  textareaRef?: (element: HTMLTextAreaElement | null) => void;
  onSave: (text: string) => void;
  onEnter?: () => void;
  onBackspaceEmpty?: () => void;
};

export function TextBlock({
  block,
  icon: Icon,
  autoFocus,
  textareaRef,
  onSave,
  onEnter,
  onBackspaceEmpty,
}: TextBlockProps) {
  const variant = VARIANTS[block.type] ?? DEFAULT_VARIANT;
  const { value, handleChange, flush } = useLocalDraft(getBlockText(block.content), onSave);

  return (
    <div className={cn("flex items-start gap-2 rounded-lg", variant.wrapperClassName)}>
      <Icon className="mt-2 size-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
      <Textarea
        ref={textareaRef}
        autoFocus={autoFocus}
        value={value}
        placeholder={variant.placeholder}
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
        className={cn(
          "min-h-0 resize-none border-none bg-transparent p-0 shadow-none focus-visible:ring-0",
          variant.textClassName,
        )}
      />
    </div>
  );
}
