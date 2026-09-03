import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { notebookApi } from "../api/notebook-api";
import { mapNotebookError } from "../lib/error-messages";
import type { Notebook, NotebookCreateInput, NotebookUpdateInput } from "../types/notebook";
import { notebookKeys } from "./query-keys";

export function useCreateNotebook(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: NotebookCreateInput) => notebookApi.create(guestId, input),
    onSuccess: (notebook) => {
      queryClient.setQueryData<Notebook[]>(notebookKeys.guest(guestId), (current) =>
        current ? [...current, notebook] : [notebook],
      );
      toast.success("تم إنشاء الدفتر");
    },
    onError: (error) => {
      toast.error(mapNotebookError(error));
    },
  });
}

export function useRenameNotebook(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ notebookId, input }: { notebookId: string; input: NotebookUpdateInput }) =>
      notebookApi.update(notebookId, input),
    onSuccess: (notebook) => {
      queryClient.setQueryData<Notebook[]>(notebookKeys.guest(guestId), (current) =>
        current?.map((item) => (item.id === notebook.id ? notebook : item)),
      );
    },
    onError: (error) => {
      toast.error(mapNotebookError(error));
    },
  });
}

export function useDeleteNotebook(guestId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notebookId: string) => notebookApi.remove(notebookId),
    onSuccess: (_data, notebookId) => {
      queryClient.setQueryData<Notebook[]>(notebookKeys.guest(guestId), (current) =>
        current?.filter((item) => item.id !== notebookId),
      );
      // Deliberately NOT removeQueries()-ing the now-invalid pages cache
      // here: the selection change this triggers unmounts/re-points the
      // component observing it on the very next render, but removeQueries
      // would evict it *immediately* while that observer is still mounted
      // with the old notebookId, which makes TanStack Query treat it as a
      // fresh query and refetch it - a GET for an already-deleted notebook
      // that 404s. Stale entries are simply garbage-collected later.
      toast.success("تم حذف الدفتر");
    },
    onError: (error) => {
      toast.error(mapNotebookError(error));
    },
  });
}
