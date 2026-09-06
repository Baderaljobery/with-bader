"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { formatMonthYear } from "../lib/date-utils";

type CalendarToolbarProps = {
  year: number;
  month: number;
  onPrevMonth: () => void;
  onNextMonth: () => void;
  onToday: () => void;
};

export function CalendarToolbar({ year, month, onPrevMonth, onNextMonth, onToday }: CalendarToolbarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-3">
        <h2 className="font-heading text-xl font-semibold text-foreground">{formatMonthYear(year, month)}</h2>
        <div className="flex items-center gap-1">
          <Button type="button" variant="outline" size="icon-sm" aria-label="الشهر السابق" onClick={onPrevMonth}>
            {/* RTL: "previous" (back in time) reads toward the right. */}
            <ChevronRight className="size-4" aria-hidden="true" />
          </Button>
          <Button type="button" variant="outline" size="icon-sm" aria-label="الشهر التالي" onClick={onNextMonth}>
            <ChevronLeft className="size-4" aria-hidden="true" />
          </Button>
        </div>
      </div>
      <Button type="button" variant="outline" size="sm" onClick={onToday}>
        اليوم
      </Button>
    </div>
  );
}
