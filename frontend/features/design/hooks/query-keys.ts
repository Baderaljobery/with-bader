export const designKeys = {
  all: ["design"] as const,
  guest: (guestId: string) => [...designKeys.all, "guest", guestId] as const,
  detail: (designId: string) => [...designKeys.all, "detail", designId] as const,
};
