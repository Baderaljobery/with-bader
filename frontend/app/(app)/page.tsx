"use client";

import { Users } from "lucide-react";
import { useState } from "react";

import { GuestFormDialog } from "@/features/guests/components/guest-form-dialog";
import { GuestGrid } from "@/features/guests/components/guest-grid";
import { useGuests } from "@/features/guests/hooks/use-guests";

export default function HomePage() {
  const [addOpen, setAddOpen] = useState(false);
  // Shares the "guests" query cache with GuestGrid (same query key) - no
  // extra network request, just a real count for the hero chip below.
  const { data: guests } = useGuests();

  return (
    <div className="space-y-8">
      <div className="relative overflow-hidden rounded-3xl border border-border bg-white px-6 py-10 sm:px-10 sm:py-12">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-24 start-1/3 size-72 rounded-full opacity-80 blur-3xl"
          style={{ backgroundImage: "var(--glow-blue)" }}
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -bottom-24 end-[-4rem] size-72 rounded-full opacity-70 blur-3xl"
          style={{ backgroundImage: "var(--glow-teal)" }}
        />

        <div className="relative flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <div className="space-y-2.5">
            <p className="text-sm font-medium text-[#1B8FEA]">مساحة العمل</p>
            <h1 className="font-heading text-4xl font-light tracking-tight text-foreground">
              مرحبًا <span className="font-bold">بدر</span> 👋
            </h1>
            <p className="max-w-md text-[15px] leading-relaxed text-muted-foreground">
              إدارة الضيوف والمقابلات في مكان واحد.
            </p>
          </div>

          {guests && guests.length > 0 ? (
            <div className="flex items-center gap-3 rounded-2xl border border-border bg-secondary/50 px-4 py-3">
              <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white">
                <Users className="size-4.5" aria-hidden="true" />
              </span>
              <div>
                <p className="text-xs text-muted-foreground">إجمالي الضيوف</p>
                <p className="font-heading text-lg font-semibold text-foreground">{guests.length}</p>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      <GuestGrid onAddGuest={() => setAddOpen(true)} />

      <GuestFormDialog open={addOpen} onOpenChange={setAddOpen} />
    </div>
  );
}
