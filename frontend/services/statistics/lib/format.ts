/** "2026-09-05" -> "5 سبتمبر". Short label for the activity chart's axis/
 * tooltip - Latin digits (same rationale as lib/format-date.ts: stable
 * numerals regardless of viewer locale), Arabic month name. */
const MONTH_LABELS_SHORT = [
  "يناير",
  "فبراير",
  "مارس",
  "أبريل",
  "مايو",
  "يونيو",
  "يوليو",
  "أغسطس",
  "سبتمبر",
  "أكتوبر",
  "نوفمبر",
  "ديسمبر",
];

export function formatShortDayMonth(isoDate: string): string {
  const date = new Date(`${isoDate}T00:00:00`);
  return `${date.getDate()} ${MONTH_LABELS_SHORT[date.getMonth()]}`;
}

/** Large numbers rendered with Latin-numeral thousands separators, e.g.
 * "1,204" - never `toLocaleString()` with the default/Arabic locale, which
 * would produce Arabic-Indic digits. */
export function formatCount(value: number): string {
  return value.toLocaleString("en-US");
}
