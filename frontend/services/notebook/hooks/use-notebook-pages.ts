import { useQuery } from "@tanstack/react-query";

import { notebookApi } from "../api/notebook-api";
import { notebookKeys } from "./query-keys";

export function useNotebookPages(notebookId: string | null) {
  return useQuery({
    queryKey: notebookKeys.pages(notebookId ?? ""),
    queryFn: () => notebookApi.listPages(notebookId as string),
    enabled: Boolean(notebookId),
  });
}
