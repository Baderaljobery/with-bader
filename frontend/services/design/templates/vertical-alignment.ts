export type VerticalAlignment = "center" | "top";

/**
 * Decides whether a text block should render vertically centered in its
 * safe content area (the calm, intentionally-composed default) or pinned
 * to the top with a fixed offset (a fallback for content long enough that
 * centering would crowd the composition or risk overflow/collision with
 * decorative elements near the edges).
 *
 * Pure and deterministic: the exact same two measured pixel heights always
 * produce the exact same result - no randomness, no manual per-slide
 * tuning. `thresholdRatio` defaults to 0.5 (within the ~45-55% "content
 * fills about half its safe area" zone where the switch should happen).
 */
export function getVerticalAlignment(
  contentHeight: number,
  availableHeight: number,
  thresholdRatio = 0.5,
): VerticalAlignment {
  if (availableHeight <= 0) return "center";
  return contentHeight / availableHeight > thresholdRatio ? "top" : "center";
}
