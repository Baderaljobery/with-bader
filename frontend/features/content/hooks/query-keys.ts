export const contentKeys = {
  all: ["content"] as const,
  guest: (guestId: string) => [...contentKeys.all, "guest", guestId] as const,
  detail: (contentId: string) => [...contentKeys.all, "detail", contentId] as const,
};
