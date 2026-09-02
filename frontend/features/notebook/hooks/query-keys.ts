export const notebookKeys = {
  all: ["notebooks"] as const,
  guest: (guestId: string) => [...notebookKeys.all, "guest", guestId] as const,
  detail: (notebookId: string) => [...notebookKeys.all, "detail", notebookId] as const,
  pages: (notebookId: string) => [...notebookKeys.all, "pages", notebookId] as const,
  blocks: (pageId: string) => [...notebookKeys.all, "blocks", pageId] as const,
};
