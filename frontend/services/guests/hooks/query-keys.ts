export const guestKeys = {
  all: ["guests"] as const,
  lists: () => [...guestKeys.all, "list"] as const,
  detail: (guestId: string) => [...guestKeys.all, "detail", guestId] as const,
  links: (guestId: string) => [...guestKeys.all, "links", guestId] as const,
};
