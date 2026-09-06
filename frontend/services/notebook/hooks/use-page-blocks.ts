import { useQuery } from "@tanstack/react-query";

import { notebookApi } from "../api/notebook-api";
import { notebookKeys } from "./query-keys";

export function usePageBlocks(pageId: string | null) {
  return useQuery({
    queryKey: notebookKeys.blocks(pageId ?? ""),
    queryFn: () => notebookApi.listBlocks(pageId as string),
    enabled: Boolean(pageId),
  });
}
