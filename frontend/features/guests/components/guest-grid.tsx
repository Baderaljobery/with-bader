"use client";

import { Search, Users } from "lucide-react";
import { useMemo, useState } from "react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useGuests } from "../hooks/use-guests";
import { AddGuestCard } from "./add-guest-card";
import { GuestCard } from "./guest-card";
import { GuestListSkeleton } from "./guest-list-skeleton";

function matchesQuery(guest: { name: string; job_title: string | null; company: string | null }, query: string) {
  const haystack = [guest.name, guest.job_title, guest.company]
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
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-sm font-semibold text-[#161616]">الضيوف</h2>
        <div className="relative w-full max-w-64">
          <Search className="absolute end-2.5 top-1/2 size-3.5 -translate-y-1/2 text-[#5F6368]" aria-hidden="true" />
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="ابحث عن ضيف..."
            aria-label="ابحث عن ضيف"
            className="pe-8"
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
