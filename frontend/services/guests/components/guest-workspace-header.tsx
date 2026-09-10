"use client";

import { Briefcase, Pencil } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { GuestFormDialog } from "./guest-form-dialog";
import type { Guest } from "../types/guest";

function initials(name: string) {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

export function GuestWorkspaceHeader({ guest }: { guest: Guest }) {
  const [editOpen, setEditOpen] = useState(false);

  return (
    <div className="relative overflow-hidden rounded-3xl border border-border bg-white px-6 py-7 sm:px-8">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-16 end-[-3rem] size-56 rounded-full opacity-70 blur-3xl"
        style={{ backgroundImage: "var(--glow-teal)" }}
      />
      <div className="relative flex flex-wrap items-start justify-between gap-5">
        <div className="flex min-w-0 flex-1 items-center gap-5">
          <div className="flex size-16 shrink-0 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-xl font-semibold text-white shadow-[0_10px_24px_-8px_rgba(27,143,234,0.5)]">
            {initials(guest.display_name) || "؟"}
          </div>
          <div className="min-w-0 flex-1 space-y-1.5 text-right">
            <div className="flex flex-wrap items-baseline gap-x-2.5">
              <h1 className="truncate font-heading text-2xl font-semibold text-[#161616]">
                {guest.display_name}
              </h1>
              {guest.name_en && guest.name_en !== guest.display_name ? (
                <span dir="ltr" className="truncate text-sm text-[#5F6368]">
                  {guest.name_en}
                </span>
              ) : null}
            </div>
            {guest.job_title || guest.company ? (
              <p className="flex items-center gap-1.5 text-sm text-[#5F6368]">
                <Briefcase className="size-3.5 shrink-0" aria-hidden="true" />
                {[guest.job_title, guest.company].filter(Boolean).join(" · ")}
              </p>
            ) : null}
          </div>
        </div>

        <Button variant="outline" size="sm" onClick={() => setEditOpen(true)}>
          <Pencil className="size-4" />
          تعديل
        </Button>
      </div>

      <GuestFormDialog open={editOpen} onOpenChange={setEditOpen} guest={guest} />
    </div>
  );
}
