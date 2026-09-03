"use client";

import { Briefcase, MoreVertical, Pencil, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DeleteGuestDialog } from "./delete-guest-dialog";
import { GuestFormDialog } from "./guest-form-dialog";
import { GuestStatusBadge } from "./guest-status-badge";
import type { Guest } from "../types/guest";

function initials(name: string) {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

export function GuestCard({ guest }: { guest: Guest }) {
  const router = useRouter();
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  return (
    <>
      <Card
        role="link"
        tabIndex={0}
        onClick={() => router.push(`/guests/${guest.id}`)}
        onKeyDown={(event) => {
          if (event.key === "Enter") router.push(`/guests/${guest.id}`);
        }}
        className="group relative cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-[var(--shadow-elevated)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
      >
        <span
          aria-hidden="true"
          className="absolute inset-x-0 top-0 h-0.5 origin-right scale-x-0 bg-[image:var(--gradient-primary)] transition-transform duration-300 group-hover:scale-x-100"
        />

        <CardHeader className="flex-row items-start justify-between gap-2 space-y-0">
          <div className="flex items-center gap-3.5">
            <div className="relative flex size-12 shrink-0 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-base font-semibold text-white shadow-[0_6px_16px_-4px_rgba(27,143,234,0.45)]">
              {initials(guest.name) || "؟"}
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-[#161616]">{guest.name}</p>
              {guest.job_title || guest.company ? (
                <p className="flex items-center gap-1 truncate text-xs text-[#5F6368]">
                  <Briefcase className="size-3 shrink-0" aria-hidden="true" />
                  {[guest.job_title, guest.company].filter(Boolean).join(" · ")}
                </p>
              ) : null}
            </div>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger
              render={
                <Button
                  variant="ghost"
                  size="icon-sm"
                  aria-label={`إجراءات ${guest.name}`}
                  onClick={(event) => event.stopPropagation()}
                />
              }
            >
              <MoreVertical className="size-4" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" onClick={(event) => event.stopPropagation()}>
              <DropdownMenuItem onClick={() => setEditOpen(true)}>
                <Pencil className="size-4" />
                تعديل
              </DropdownMenuItem>
              <DropdownMenuItem variant="destructive" onClick={() => setDeleteOpen(true)}>
                <Trash2 className="size-4" />
                حذف
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </CardHeader>

        <CardContent>
          <GuestStatusBadge status={guest.preparation_status} />
        </CardContent>
      </Card>

      <GuestFormDialog open={editOpen} onOpenChange={setEditOpen} guest={guest} />
      <DeleteGuestDialog open={deleteOpen} onOpenChange={setDeleteOpen} guest={guest} />
    </>
  );
}
