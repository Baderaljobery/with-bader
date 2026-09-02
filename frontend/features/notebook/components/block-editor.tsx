"use client";

import {
  closestCenter,
  DndContext,
  type DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  sortableKeyboardCoordinates,
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Plus } from "lucide-react";
import { useRef, useState } from "react";

import { ErrorState } from "@/components/shared/error-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  useCreateBlock,
  useDeleteBlock,
  useReorderBlock,
  useUpdateBlock,
} from "../hooks/use-block-mutations";
import { usePageBlocks } from "../hooks/use-page-blocks";
import { contentForTypeChange } from "../lib/block-conversion";
import { getBlockTypeMeta } from "../lib/block-types";
import { nextBlockPosition, positionForIndex } from "../lib/position";
import type { Block, BlockType, ChecklistItem } from "../types/block";
import { BlockToolbar } from "./block-toolbar";
import { ChecklistBlock } from "./blocks/checklist-block";
import { DividerBlock } from "./blocks/divider-block";
import { ListBlock } from "./blocks/list-block";
import { QuestionBlock } from "./blocks/question-block";
import { TextBlock } from "./blocks/text-block";

type SortableBlockRowProps = {
  block: Block;
  guestId: string;
  autoFocus: boolean;
  registerFocusRef: (blockId: string, element: HTMLTextAreaElement | null) => void;
  onInsert: (type: BlockType) => void;
  onChangeType: (type: BlockType) => void;
  onDelete: () => void;
  onSaveContent: (content: Record<string, unknown>) => void;
  onLinkQuestion: (questionId: string | null) => void;
  onEnter: () => void;
  onBackspaceEmpty: () => void;
};

function SortableBlockRow({
  block,
  guestId,
  autoFocus,
  registerFocusRef,
  onInsert,
  onChangeType,
  onDelete,
  onSaveContent,
  onLinkQuestion,
  onEnter,
  onBackspaceEmpty,
}: SortableBlockRowProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: block.id,
  });

  const style = { transform: CSS.Transform.toString(transform), transition };
  const meta = getBlockTypeMeta(block.type);

  let content: React.ReactNode;
  if (block.type === "divider") {
    content = <DividerBlock />;
  } else if (block.type === "bullet_list" || block.type === "numbered_list") {
    content = (
      <ListBlock
        block={block}
        ordered={block.type === "numbered_list"}
        autoFocus={autoFocus}
        onSave={(items) => onSaveContent({ items })}
      />
    );
  } else if (block.type === "checklist") {
    content = (
      <ChecklistBlock
        block={block}
        autoFocus={autoFocus}
        onSave={(items: ChecklistItem[]) => onSaveContent({ items })}
      />
    );
  } else if (block.type === "question") {
    content = (
      <QuestionBlock
        block={block}
        guestId={guestId}
        autoFocus={autoFocus}
        textareaRef={(element) => registerFocusRef(block.id, element)}
        onSaveText={(text) => onSaveContent({ text })}
        onLink={onLinkQuestion}
        onEnter={onEnter}
        onBackspaceEmpty={onBackspaceEmpty}
      />
    );
  } else {
    content = (
      <TextBlock
        block={block}
        icon={meta.icon}
        autoFocus={autoFocus}
        textareaRef={(element) => registerFocusRef(block.id, element)}
        onSave={(text) => onSaveContent({ text })}
        onEnter={onEnter}
        onBackspaceEmpty={onBackspaceEmpty}
      />
    );
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        "group/block relative -mx-1 flex items-start gap-1 rounded-lg px-1 py-0.5",
        isDragging && "z-10 bg-background opacity-70 shadow-md",
      )}
    >
      <BlockToolbar
        currentType={block.type}
        dragAttributes={attributes}
        dragListeners={listeners}
        onInsert={onInsert}
        onChangeType={onChangeType}
        onDelete={onDelete}
      />
      <div className="min-w-0 flex-1 py-1">{content}</div>
    </div>
  );
}

type BlockEditorProps = {
  pageId: string;
  guestId: string;
};

export function BlockEditor({ pageId, guestId }: BlockEditorProps) {
  const blocksQuery = usePageBlocks(pageId);
  const createBlock = useCreateBlock(pageId);
  const updateBlock = useUpdateBlock(pageId);
  const deleteBlock = useDeleteBlock(pageId);
  const reorderBlock = useReorderBlock(pageId);

  const [focusBlockId, setFocusBlockId] = useState<string | null>(null);
  const focusRefs = useRef(new Map<string, HTMLTextAreaElement>());

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  function registerFocusRef(blockId: string, element: HTMLTextAreaElement | null) {
    if (element) {
      focusRefs.current.set(blockId, element);
    } else {
      focusRefs.current.delete(blockId);
    }
  }

  function focusPreviousBlock(previousBlockId: string | undefined) {
    if (!previousBlockId) return;
    const element = focusRefs.current.get(previousBlockId);
    if (!element) return;
    element.focus();
    const end = element.value.length;
    element.setSelectionRange(end, end);
  }

  if (blocksQuery.isPending) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-6 w-2/3" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  if (blocksQuery.isError) {
    return (
      <ErrorState
        title="تعذر تحميل محتوى الصفحة"
        description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
        onRetry={() => blocksQuery.refetch()}
      />
    );
  }

  const blocks = blocksQuery.data;

  function insertBlockAt(index: number, type: BlockType) {
    const meta = getBlockTypeMeta(type);
    const position = positionForIndex(blocks, index);
    createBlock.mutate(
      { type, content: meta.defaultContent(), position },
      { onSuccess: (block) => setFocusBlockId(block.id) },
    );
  }

  function appendBlock(type: BlockType = "paragraph") {
    const meta = getBlockTypeMeta(type);
    createBlock.mutate(
      { type, content: meta.defaultContent(), position: nextBlockPosition(blocks) },
      { onSuccess: (block) => setFocusBlockId(block.id) },
    );
  }

  function handleChangeType(block: Block, newType: BlockType) {
    updateBlock.mutate({
      blockId: block.id,
      input: {
        type: newType,
        content: contentForTypeChange(block, newType),
        linked_question_id: newType === "question" ? block.linked_question_id : null,
      },
    });
  }

  function handleBackspaceEmpty(block: Block, index: number) {
    const previousBlockId = blocks[index - 1]?.id;
    deleteBlock.mutate(block.id);
    focusPreviousBlock(previousBlockId);
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = blocks.findIndex((block) => block.id === active.id);
    const newIndex = blocks.findIndex((block) => block.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;

    const reordered = arrayMove(blocks, oldIndex, newIndex);
    const movedIndex = reordered.findIndex((block) => block.id === active.id);
    const neighbors = reordered.filter((_, index) => index !== movedIndex);
    const position = positionForIndex(neighbors, movedIndex);

    reorderBlock.mutate({
      blockId: active.id as string,
      position,
      reorderedIds: reordered.map((block) => block.id),
    });
  }

  if (blocks.length === 0) {
    return (
      <button
        type="button"
        onClick={() => appendBlock("paragraph")}
        className="w-full rounded-lg border border-dashed border-border px-3 py-6 text-start text-sm text-muted-foreground transition-colors hover:border-primary/40 hover:bg-secondary/40"
      >
        ابدأ الكتابة...
      </button>
    );
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={blocks.map((block) => block.id)} strategy={verticalListSortingStrategy}>
        <div className="space-y-0.5">
          {blocks.map((block, index) => (
            <SortableBlockRow
              key={block.id}
              block={block}
              guestId={guestId}
              autoFocus={block.id === focusBlockId}
              registerFocusRef={registerFocusRef}
              onInsert={(type) => insertBlockAt(index + 1, type)}
              onChangeType={(type) => handleChangeType(block, type)}
              onDelete={() => deleteBlock.mutate(block.id)}
              onSaveContent={(content) => updateBlock.mutate({ blockId: block.id, input: { content } })}
              onLinkQuestion={(questionId) =>
                updateBlock.mutate({ blockId: block.id, input: { linked_question_id: questionId } })
              }
              onEnter={() => insertBlockAt(index + 1, "paragraph")}
              onBackspaceEmpty={() => handleBackspaceEmpty(block, index)}
            />
          ))}
        </div>
      </SortableContext>

      <button
        type="button"
        onClick={() => appendBlock("paragraph")}
        className="mt-1 flex w-full items-center gap-1.5 rounded-lg px-1 py-1.5 text-start text-xs text-muted-foreground transition-colors hover:bg-secondary/60"
      >
        <Plus className="size-3.5" aria-hidden="true" />
        إضافة كتلة
      </button>
    </DndContext>
  );
}
