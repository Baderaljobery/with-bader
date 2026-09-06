"use client";

import { Building2, CalendarPlus, RefreshCw } from "lucide-react";
import { useParams } from "next/navigation";
import type { LucideIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ContentStatusSelect } from "@/services/guests/components/content-status-select";
import { useGuest } from "@/services/guests/hooks/use-guest";

function formatDate(value: string) {
  // Fixed locale (not `undefined`/browser locale) so dates render with
  // stable Latin numerals regardless of the viewer's OS/browser language -
  // ar locales format Gregorian dates with Arabic-Indic digits, which
  // collide visually next to the surrounding Arabic copy.
  return new Date(value).toLocaleDateString("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function InfoChip({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <Card size="sm">
      <CardContent className="flex items-center gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-[image:var(--gradient-primary)] text-white shadow-[0_6px_14px_-4px_rgba(27,143,234,0.4)]">
          <Icon className="size-4.5" aria-hidden="true" />
        </span>
        <div className="min-w-0">
          <p className="text-xs text-[#5F6368]">{label}</p>
          <p className="truncate text-sm font-medium text-[#161616]">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function GuestOverviewPage() {
  const { guestId } = useParams<{ guestId: string }>();
  const { data: guest, isPending } = useGuest(guestId);

  if (isPending || !guest) {
    return <Skeleton className="h-40 w-full" />;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <InfoChip
          icon={Building2}
          label="الشركة"
          value={guest.company ?? "—"}
        />
        <ContentStatusSelect guest={guest} />
        <InfoChip icon={CalendarPlus} label="تاريخ الإضافة" value={formatDate(guest.created_at)} />
        <InfoChip icon={RefreshCw} label="آخر تحديث" value={formatDate(guest.updated_at)} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>نبذة تعريفية</CardTitle>
          </CardHeader>
          <CardContent>
            {guest.biography ? (
              <p className="whitespace-pre-wrap text-sm text-[#161616]">{guest.biography}</p>
            ) : (
              <p className="text-sm text-[#5F6368]">لا توجد نبذة تعريفية بعد.</p>
            )}
          </CardContent>
        </Card>

        {guest.research_summary ? (
          <Card>
            <CardHeader>
              <CardTitle>ملخص البحث</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap text-sm text-[#161616]">{guest.research_summary}</p>
            </CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
