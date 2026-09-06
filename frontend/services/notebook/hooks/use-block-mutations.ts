import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { notebookApi } from "../api/notebook-api";
import { mapNotebookError } from "../lib/error-messages";
import type { Block, BlockCreateInput, BlockUpdateInput } from "../types/block";
import { notebookKeys } from "./query-keys";

/** Watched by page-header.tsx to show a subtle "جارٍ الحفظ..." indicator
 * without wiring per-block save state through props. */
export const BLOCK_CONTENT_SAVE_MUTATION_KEY = "notebook-update-block-content";

type BlockMutationContext = { previous: Block[] | undefined };

export function useCreateBlock(pageId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: BlockCreateInput) => notebookApi.createBlock(pageId, input),
    onSuccess: (block) => {
      queryClient.setQueryData<Block[]>(notebookKeys.blocks(pageId), (current) =>
        current ? [...current, block].sort((a, b) => a.position - b.position) : [block],
      );
    },
    onError: (error) => {
      toast.error(mapNotebookError(error));
    },
  });
}

/** Powers autosave (debounced content edits), type changes, and
 * link/unlink-question - all go through PATCH /api/blocks/{id}. Optimistic
 * so typing never waits on a round-trip, with rollback on failure so a
 * failed save doesn't silently keep wrong data on screen. */
export function useUpdateBlock(pageId: string) {
  const queryClient = useQueryClient();

  return useMutation<
    Block,
    unknown,
    { blockId: string; input: BlockUpdateInput },
    BlockMutationContext
  >({
    mutationKey: [BLOCK_CONTENT_SAVE_MUTATION_KEY, pageId],
    mutationFn: ({ blockId, input }) => notebookApi.updateBlock(blockId, input),
    onMutate: async ({ blockId, input }) => {
      await queryClient.cancelQueries({ queryKey: notebookKeys.blocks(pageId) });
      const previous = queryClient.getQueryData<Block[]>(notebookKeys.blocks(pageId));
      queryClient.setQueryData<Block[]>(notebookKeys.blocks(pageId), (current) =>
        current?.map((block) => (block.id === blockId ? { ...block, ...input } : block)),
      );
      return { previous };
    },
    onError: (error, _variables, context) => {
      if (context) {
        queryClient.setQueryData(notebookKeys.blocks(pageId), context.previous);
      }
      toast.error(mapNotebookError(error));
    },
    onSuccess: (block) => {
      queryClient.setQueryData<Block[]>(notebookKeys.blocks(pageId), (current) =>
        current?.map((item) => (item.id === block.id ? block : item)),
      );
    },
  });
}

export function useDeleteBlock(pageId: string) {
  const queryClient = useQueryClient();

  return useMutation<void, unknown, string, BlockMutationContext>({
    mutationFn: (blockId: string) => notebookApi.removeBlock(blockId),
    onMutate: async (blockId) => {
      await queryClient.cancelQueries({ queryKey: notebookKeys.blocks(pageId) });
      const previous = queryClient.getQueryData<Block[]>(notebookKeys.blocks(pageId));
      queryClient.setQueryData<Block[]>(notebookKeys.blocks(pageId), (current) =>
        current?.filter((block) => block.id !== blockId),
      );
      return { previous };
    },
    onError: (error, _variables, context) => {
      if (context) {
        queryClient.setQueryData(notebookKeys.blocks(pageId), context.previous);
      }
      toast.error(mapNotebookError(error));
    },
  });
}

/** Drag-and-drop reorder. `reorderedIds` is the full, already-locally-moved
 * id order (see block-editor.tsx's onDragEnd) - the cache is written in
 * that exact order so the UI never snaps back while the PATCH for the
 * moved block's new fractional position is in flight. */
export function useReorderBlock(pageId: string) {
  const queryClient = useQueryClient();

  return useMutation<
    Block,
    unknown,
    { blockId: string; position: number; reorderedIds: string[] },
    BlockMutationContext
  >({
    mutationFn: ({ blockId, position }) => notebookApi.updateBlock(blockId, { position }),
    onMutate: async ({ blockId, position, reorderedIds }) => {
      await queryClient.cancelQueries({ queryKey: notebookKeys.blocks(pageId) });
      const previous = queryClient.getQueryData<Block[]>(notebookKeys.blocks(pageId));
      if (previous) {
        const byId = new Map(previous.map((block) => [block.id, block]));
        const next = reorderedIds
          .map((id) => byId.get(id))
          .filter((block): block is Block => Boolean(block))
          .map((block) => (block.id === blockId ? { ...block, position } : block));
        queryClient.setQueryData<Block[]>(notebookKeys.blocks(pageId), next);
      }
      return { previous };
    },
    onError: (error, _variables, context) => {
      if (context) {
        queryClient.setQueryData(notebookKeys.blocks(pageId), context.previous);
      }
      toast.error(mapNotebookError(error));
    },
  });
}
