export const researchKeys = {
  all: ["guest-research"] as const,
  latest: (guestId: string) => [...researchKeys.all, "latest", guestId] as const,
  history: (guestId: string) => [...researchKeys.all, "history", guestId] as const,
  detail: (researchId: string) => [...researchKeys.all, "detail", researchId] as const,
};
