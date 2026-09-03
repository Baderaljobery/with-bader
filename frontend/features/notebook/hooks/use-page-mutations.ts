import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { notebookApi } from "../api/notebook-api";
import { mapNotebookError } from "../lib/error-messages";
import type {
  NotebookPage,
  NotebookPageCreateInput,
  NotebookPageUpdateInput,
} from "../types/notebook-page";
import { notebookKeys } from "./query-keys";

export function useCreatePage(notebookId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: NotebookPageCreateInput) => notebookApi.createPage(notebookId, input),
    onSuccess: (page) => {
      queryClient.setQueryData<NotebookPage[]>(notebookKeys.pages(notebookId), (current) =>
        current ? [...current, page].sort((a, b) => a.position - b.position) : [page],
      );
    },
    onError: (error) => {
      toast.error(mapNotebookError(error));
    },
  });
}

export function useRenamePage(notebookId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ pageId, input }: { pageId: string; input: NotebookPageUpdateInput }) =>
      notebookApi.updatePage(pageId, input),
    onSuccess: (page) => {
      queryClient.setQueryData<NotebookPage[]>(notebookKeys.pages(notebookId), (current) =>
        current?.map((item) => (item.id === page.id ? page : item)),
      );
    },
    onError: (error) => {
      toast.error(mapNotebookError(error));
    },
  });
}

export function useDeletePage(notebookId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (pageId: string) => notebookApi.removePage(pageId),
    onSuccess: (_data, pageId) => {
      queryClient.setQueryData<NotebookPage[]>(notebookKeys.pages(notebookId), (current) =>
        current?.filter((item) => item.id !== pageId),
      );
      // Deliberately NOT removeQueries()-ing the now-invalid blocks cache
      // here - see the matching comment in use-notebook-mutations.ts: an
      // active BlockEditor still observing this exact pageId (e.g. deleting
      // the currently-open page) would have its query evicted and
      // immediately refetched for an already-deleted page, which 404s.
      toast.success("تم حذف الصفحة");
    },
    onError: (error) => {
      toast.error(mapNotebookError(error));
    },
  });
}
