import { Briefcase } from "lucide-react";

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

export function GuestWorkspaceHeader({ guest }: { guest: Guest }) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      <div className="flex size-14 shrink-0 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-lg font-semibold text-white">
        {initials(guest.name) || "؟"}
      </div>
      <div className="min-w-0 flex-1 space-y-1">
        <h1 className="truncate font-heading text-xl font-semibold text-[#161616]">
          {guest.name}
        </h1>
        {guest.job_title || guest.company ? (
          <p className="flex items-center gap-1.5 text-sm text-[#5F6368]">
            <Briefcase className="size-3.5 shrink-0" aria-hidden="true" />
            {[guest.job_title, guest.company].filter(Boolean).join(" · ")}
          </p>
        ) : null}
      </div>
      <GuestStatusBadge status={guest.preparation_status} />
    </div>
  );
}
