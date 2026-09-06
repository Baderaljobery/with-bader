export const questionKeys = {
  all: ["questions"] as const,
  guest: (guestId: string) => [...questionKeys.all, "guest", guestId] as const,
  detail: (questionId: string) => [...questionKeys.all, "detail", questionId] as const,
  versions: (questionId: string) => [...questionKeys.all, "versions", questionId] as const,
};
