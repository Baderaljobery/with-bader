/** A restrained set of With Bader-compatible card treatments, derived only
 * from the approved palette in design-notes.md (teal/blue gradient ends +
 * wordmark navy + neutral) - never a color outside that table. Four
 * coordinated tones, not one-color-per-card. */
export const STAT_THEME = {
  navy: {
    background: "#0B1F3A",
    text: "#FFFFFF",
    subtleText: "rgba(255,255,255,0.72)",
    accent: "#1FCFC3",
  },
  teal: {
    background: "#EAFBFA",
    text: "#0F766E",
    subtleText: "#5F8C89",
    accent: "#1FCFC3",
  },
  blue: {
    background: "#EAF4FE",
    text: "#155E9E",
    subtleText: "#5C7C97",
    accent: "#1B8FEA",
  },
  neutral: {
    background: "#F7F8FA",
    text: "#161616",
    subtleText: "#5F6368",
    accent: "#5F6368",
  },
} as const;

export type StatTone = keyof typeof STAT_THEME;
