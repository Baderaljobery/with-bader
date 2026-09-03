export const interviewKeys = {
  all: ["interview"] as const,
  transcript: (guestId: string) => [...interviewKeys.all, "transcript", guestId] as const,
};
