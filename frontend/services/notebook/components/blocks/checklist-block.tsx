"use client";

import { Plus } from "lucide-react";
import { useMemo, useRef } from "react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useLocalDraft } from "../../hooks/use-local-draft";
import { getChecklistItems } from "../../lib/block-content";
import type { Block, ChecklistItem } from "../../types/block";

type ChecklistBlockProps = {
  block: Block;
  autoFocus?: boolean;
  onSave: (items: ChecklistItem[]) => void;
};

export function ChecklistBlock({ block, autoFocus, onSave }: ChecklistBlockProps) {
  // See list-block.tsx for why this must be memoized on block.content -
  // useLocalDraft compares serverValue by reference, and an unmemoized
  // array literal here would be "changed" on every render forever.
  const serverItems = useMemo(() => {
    const items = getChecklistItems(block.content);
    return items.length > 0 ? items : [{ text: "", checked: false }];
  }, [block.content]);
  const { value, handleChange, flush } = useLocalDraft(serverItems, onSave);
  const inputRefs = useRef<Array<HTMLInputElement | null>>([]);

  function updateItem(index: number, patch: Partial<ChecklistItem>) {
    const next = value.map((item, itemIndex) => (itemIndex === index ? { ...item, ...patch } : item));
    handleChange(next);
  }

  function addItemAfter(index: number) {
    const next = [...value];
    next.splice(index + 1, 0, { text: "", checked: false });
    handleChange(next);
    flush();
    requestAnimationFrame(() => inputRefs.current[index + 1]?.focus());
  }

  function removeItem(index: number) {
    if (value.length <= 1) {
      handleChange([{ text: "", checked: false }]);
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
          <Checkbox
            checked={item.checked}
            onCheckedChange={(checked) => {
              updateItem(index, { checked: checked === true });
              flush();
            }}
            aria-label="إتمام المهمة"
          />
          <Input
            ref={(element) => {
              inputRefs.current[index] = element;
            }}
            autoFocus={autoFocus && index === 0}
            value={item.text}
            onChange={(event) => updateItem(index, { text: event.target.value })}
            onBlur={flush}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                addItemAfter(index);
              } else if (event.key === "Backspace" && item.text === "" && value.length > 1) {
                event.preventDefault();
                removeItem(index);
              }
            }}
            placeholder="مهمة جديدة"
            className={cn(
              "h-7 border-none bg-transparent px-0 shadow-none focus-visible:ring-0",
              item.checked && "text-muted-foreground line-through",
            )}
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
        إضافة مهمة
      </Button>
    </div>
  );
}
