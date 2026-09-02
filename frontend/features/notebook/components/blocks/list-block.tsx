"use client";

import { Plus } from "lucide-react";
import { useMemo, useRef } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLocalDraft } from "../../hooks/use-local-draft";
import { getBlockItems } from "../../lib/block-content";
import type { Block } from "../../types/block";

type ListBlockProps = {
  block: Block;
  ordered: boolean;
  autoFocus?: boolean;
  onSave: (items: string[]) => void;
};

export function ListBlock({ block, ordered, autoFocus, onSave }: ListBlockProps) {
  // Memoized on block.content (not recomputed on every render): useLocalDraft
  // compares serverValue by reference, and getBlockItems(...).filter(...)
  // returns a brand-new array every call. Without this memo, an unchanged
  // block.content would still produce a "changed" serverValue on every
  // render, and useLocalDraft's render-time sync would write state on every
  // render forever - the loop this component was hit by.
  const serverItems = useMemo(() => {
    const items = getBlockItems(block.content);
    return items.length > 0 ? items : [""];
  }, [block.content]);
  const { value, handleChange, flush } = useLocalDraft(serverItems, onSave);
  const inputRefs = useRef<Array<HTMLInputElement | null>>([]);

  function updateItem(index: number, text: string) {
    const next = [...value];
    next[index] = text;
    handleChange(next);
  }

  function addItemAfter(index: number) {
    const next = [...value];
    next.splice(index + 1, 0, "");
    handleChange(next);
    flush();
    requestAnimationFrame(() => inputRefs.current[index + 1]?.focus());
  }

  function removeItem(index: number) {
    if (value.length <= 1) {
      handleChange([""]);
      flush();
      return;
    }
    const next = value.filter((_, itemIndex) => itemIndex !== index);
    handleChange(next);
    flush();
    requestAnimationFrame(() => inputRefs.current[Math.max(0, index - 1)]?.focus());
  }

  return (
    <div className="space-y-1">
      {value.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          <span className="w-4 shrink-0 text-center text-sm text-muted-foreground" aria-hidden="true">
            {ordered ? `${index + 1}.` : "•"}
          </span>
          <Input
            ref={(element) => {
              inputRefs.current[index] = element;
            }}
            autoFocus={autoFocus && index === 0}
            value={item}
            onChange={(event) => updateItem(index, event.target.value)}
            onBlur={flush}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                addItemAfter(index);
              } else if (event.key === "Backspace" && item === "" && value.length > 1) {
                event.preventDefault();
                removeItem(index);
              }
            }}
            placeholder="عنصر جديد"
            className="h-7 border-none bg-transparent px-0 shadow-none focus-visible:ring-0"
          />
        </div>
      ))}
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-6 px-1.5 text-xs text-muted-foreground"
        onClick={() => addItemAfter(value.length - 1)}
      >
        <Plus className="size-3" aria-hidden="true" />
        إضافة عنصر
      </Button>
    </div>
  );
}
