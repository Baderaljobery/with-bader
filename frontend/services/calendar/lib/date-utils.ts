import { MONTH_LABELS, WEEKDAY_LABELS } from "./labels";

export type CalendarDayInfo = {
  date: Date;
  /** "YYYY-MM-DD", built from local date parts (never `toISOString()`,
   * which shifts to UTC and can land on the wrong day). */
  isoDate: string;
  inCurrentMonth: boolean;
  isToday: boolean;
};

function toIsoDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** Always exactly 6 weeks (42 days) so the grid's height never shifts
 * between months - includes the leading/trailing days from the adjacent
 * months needed to fill out the first and last weeks. */
export function getMonthGrid(year: number, monthIndex: number): CalendarDayInfo[] {
  const firstOfMonth = new Date(year, monthIndex, 1);
  const gridStart = new Date(year, monthIndex, 1 - firstOfMonth.getDay());
  const todayIso = toIsoDate(new Date());

  return Array.from({ length: 42 }, (_, i) => {
    const date = new Date(gridStart.getFullYear(), gridStart.getMonth(), gridStart.getDate() + i);
    const isoDate = toIsoDate(date);
    return {
      date,
      isoDate,
      inCurrentMonth: date.getMonth() === monthIndex && date.getFullYear() === year,
      isToday: isoDate === todayIso,
    };
  });
}

export function formatMonthYear(year: number, monthIndex: number): string {
  return `${MONTH_LABELS[monthIndex]} ${year}`;
}

/** "14:30" -> "2:30 م". Latin digits throughout (same rationale as
 * lib/format-date.ts: stable numerals regardless of viewer locale). */
export function formatTimeArabic(time: string): string {
  const [hoursStr, minutesStr] = time.split(":");
  const hours24 = Number(hoursStr);
  const period = hours24 >= 12 ? "م" : "ص";
  const hours12 = hours24 % 12 === 0 ? 12 : hours24 % 12;
  return `${hours12}:${minutesStr} ${period}`;
}

/** "2026-09-10" -> "الخميس، 10 سبتمبر 2026". */
export function formatFullDateArabic(isoDate: string): string {
  const date = new Date(`${isoDate}T00:00:00`);
  const weekday = WEEKDAY_LABELS[date.getDay()];
  const month = MONTH_LABELS[date.getMonth()];
  return `${weekday}، ${date.getDate()} ${month} ${date.getFullYear()}`;
}
