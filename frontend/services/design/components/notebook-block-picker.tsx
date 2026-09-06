"use client";

import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { getBlockText } from "@/services/notebook/lib/block-content";
import { useGuestNotebookBlocks } from "../hooks/use-guest-notebook-blocks";

type NotebookBlockPickerProps = {
  guestId: string;
  value: string[];
  onChange: (blockIds: string[]) => void;
  disabled?: boolean;
};

/** Only real, text-bearing notebook blocks are listed and selectable - the
 * user explicitly picks which ones to use as supporting context, nothing
 * is included automatically. */
export function NotebookBlockPicker({ guestId, value, onChange, disabled }: NotebookBlockPickerProps) {
  const { data: blocks, isPending } = useGuestNotebookBlocks(guestId);

  if (isPending) {
    return <Skeleton className="h-16 w-full" />;
  }

  const withText = (blocks ?? []).filter((block) => getBlockText(block.content).trim().length > 0);

  if (withText.length === 0) {
    return <p className="text-sm text-muted-foreground">لا توجد ملاحظات في الدفتر لاستخدامها كمصدر داعم.</p>;
  }

  function toggle(blockId: string, checked: boolean) {
    onChange(checked ? [...value, blockId] : value.filter((id) => id !== blockId));
  }

  return (
    <div className="max-h-56 space-y-1 overflow-y-auto rounded-2xl border border-border p-2">
      {withText.map((block) => {
        const checked = value.includes(block.id);
        return (
          <label
            key={block.id}
            className="flex cursor-pointer items-start gap-2.5 rounded-xl px-2.5 py-2 text-sm hover:bg-secondary/60"
          >
            <Checkbox
              checked={checked}
              onCheckedChange={(next) => toggle(block.id, next === true)}
              disabled={disabled}
              className="mt-0.5"
            />
            <span className="line-clamp-2 text-foreground">{getBlockText(block.content)}</span>
          </label>
        );
      })}
    </div>
  );
}
