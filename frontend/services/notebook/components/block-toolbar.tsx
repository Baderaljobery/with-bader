"use client";

import type { DraggableAttributes } from "@dnd-kit/core";
import type { SyntheticListenerMap } from "@dnd-kit/core/dist/hooks/utilities";
import { GripVertical, MoreVertical, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { BlockTypeMenu } from "./block-type-menu";
import type { BlockType } from "../types/block";

type BlockToolbarProps = {
  currentType: BlockType;
  dragAttributes: DraggableAttributes;
  dragListeners: SyntheticListenerMap | undefined;
  onInsert: (type: BlockType) => void;
  onChangeType: (type: BlockType) => void;
  onDelete: () => void;
};

export function BlockToolbar({
  currentType,
  dragAttributes,
  dragListeners,
  onInsert,
  onChangeType,
  onDelete,
}: BlockToolbarProps) {
  return (
    <div className="flex shrink-0 items-center gap-0.5 pt-1 opacity-0 transition-opacity group-hover/block:opacity-100 group-focus-within/block:opacity-100">
      <DropdownMenu>
        <DropdownMenuTrigger
          render={<Button type="button" variant="ghost" size="icon-xs" aria-label="إضافة كتلة" />}
        >
          <Plus className="size-3.5" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <BlockTypeMenu onSelect={onInsert} />
        </DropdownMenuContent>
      </DropdownMenu>

      <button
        type="button"
        aria-label="سحب لإعادة الترتيب"
        className="flex size-6 cursor-grab touch-none items-center justify-center rounded-md text-muted-foreground hover:bg-muted active:cursor-grabbing"
        {...dragAttributes}
        {...dragListeners}
      >
        <GripVertical className="size-3.5" />
      </button>

      <DropdownMenu>
        <DropdownMenuTrigger
          render={<Button type="button" variant="ghost" size="icon-xs" aria-label="خيارات الكتلة" />}
        >
          <MoreVertical className="size-3.5" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuSub>
            <DropdownMenuSubTrigger>تغيير النوع</DropdownMenuSubTrigger>
            <DropdownMenuSubContent>
              <BlockTypeMenu onSelect={onChangeType} disabledType={currentType} />
            </DropdownMenuSubContent>
          </DropdownMenuSub>
          <DropdownMenuSeparator />
          <DropdownMenuItem variant="destructive" onClick={onDelete}>
            <Trash2 className="size-3.5" />
            حذف
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
