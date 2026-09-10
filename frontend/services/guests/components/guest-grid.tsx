"use client";

import { Search, Users } from "lucide-react";
import { useMemo, useState } from "react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useGuests } from "../hooks/use-guests";
import type { Guest } from "../types/guest";
import { AddGuestCard } from "./add-guest-card";
import { GuestCard } from "./guest-card";
import { GuestListSkeleton } from "./guest-list-skeleton";

// Bilingual (Phase 4) - matches both the Arabic and English name so a
// query in either language finds the guest, regardless of which language
// the visible card happens to be showing. company/job_title stay the
// existing single-value fields.
function matchesQuery(guest: Guest, query: string) {
  const haystack = [guest.name_ar, guest.name_en, guest.name, guest.company, guest.job_title]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return haystack.includes(query.toLowerCase());
}

export function GuestGrid({ onAddGuest }: { onAddGuest: () => void }) {
  const { data: guests, isPending, isError, refetch } = useGuests();
  const [query, setQuery] = useState("");

  const filteredGuests = useMemo(() => {
    if (!guests) return [];
    if (!query.trim()) return guests;
    return guests.filter((guest) => matchesQuery(guest, query.trim()));
  }, [guests, query]);

  if (isPending) {
    return <GuestListSkeleton />;
  }

  if (isError) {
    return (
      <ErrorState
        title="تعذر تحميل الضيوف"
        description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
        onRetry={() => refetch()}
      />
    );
  }

  if (guests.length === 0) {
    return (
      <EmptyState
        icon={Users}
        title="لا يوجد ضيوف بعد"
        description="أضف أول ضيف لتبدأ بالبحث عنه وتحضير الأسئلة."
        action={<Button onClick={onAddGuest}>إضافة ضيف</Button>}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="font-heading text-lg font-semibold text-foreground">الضيوف</h2>
        <div className="relative w-full sm:max-w-80">
          <Search
            className="absolute end-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden="true"
          />
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="ابحث عن ضيف بالاسم أو الشركة..."
            aria-label="ابحث عن ضيف"
            className="h-11 rounded-full border-border bg-white pe-10 shadow-[var(--shadow-soft)]"
          />
        </div>
      </div>

      {filteredGuests.length === 0 ? (
        <EmptyState
          icon={Search}
          title="لا توجد نتائج"
          description="جرّب كلمة بحث مختلفة."
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <AddGuestCard onClick={onAddGuest} />
          {filteredGuests.map((guest) => (
            <GuestCard key={guest.id} guest={guest} />
          ))}
        </div>
      )}
    </div>
  );
}
