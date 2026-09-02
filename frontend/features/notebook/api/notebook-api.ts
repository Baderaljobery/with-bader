import { apiClient } from "@/lib/api/client";
import type { Block, BlockCreateInput, BlockUpdateInput } from "../types/block";
import type { Notebook, NotebookCreateInput, NotebookUpdateInput } from "../types/notebook";
import type {
  NotebookPage,
  NotebookPageCreateInput,
  NotebookPageUpdateInput,
} from "../types/notebook-page";

export const notebookApi = {
  list: (guestId: string): Promise<Notebook[]> =>
    apiClient.get<Notebook[]>(`/api/guests/${guestId}/notebooks`),
  create: (guestId: string, input: NotebookCreateInput): Promise<Notebook> =>
    apiClient.post<Notebook>(`/api/guests/${guestId}/notebooks`, input),
  update: (notebookId: string, input: NotebookUpdateInput): Promise<Notebook> =>
    apiClient.patch<Notebook>(`/api/notebooks/${notebookId}`, input),
  remove: (notebookId: string): Promise<void> =>
    apiClient.delete<void>(`/api/notebooks/${notebookId}`),

  listPages: (notebookId: string): Promise<NotebookPage[]> =>
    apiClient.get<NotebookPage[]>(`/api/notebooks/${notebookId}/pages`),
  createPage: (notebookId: string, input: NotebookPageCreateInput): Promise<NotebookPage> =>
    apiClient.post<NotebookPage>(`/api/notebooks/${notebookId}/pages`, input),
  updatePage: (pageId: string, input: NotebookPageUpdateInput): Promise<NotebookPage> =>
    apiClient.patch<NotebookPage>(`/api/notebook-pages/${pageId}`, input),
  removePage: (pageId: string): Promise<void> =>
    apiClient.delete<void>(`/api/notebook-pages/${pageId}`),

  listBlocks: (pageId: string): Promise<Block[]> =>
    apiClient.get<Block[]>(`/api/notebook-pages/${pageId}/blocks`),
  createBlock: (pageId: string, input: BlockCreateInput): Promise<Block> =>
    apiClient.post<Block>(`/api/notebook-pages/${pageId}/blocks`, input),
  updateBlock: (blockId: string, input: BlockUpdateInput): Promise<Block> =>
    apiClient.patch<Block>(`/api/blocks/${blockId}`, input),
  removeBlock: (blockId: string): Promise<void> =>
    apiClient.delete<void>(`/api/blocks/${blockId}`),
};
