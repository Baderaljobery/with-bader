import { Briefcase } from "lucide-react";

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
    <div className="relative overflow-hidden rounded-3xl border border-border bg-white px-6 py-7 sm:px-8">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-16 end-[-3rem] size-56 rounded-full opacity-70 blur-3xl"
        style={{ backgroundImage: "var(--glow-teal)" }}
      />
      <div className="relative flex flex-wrap items-center gap-5">
        <div className="flex size-16 shrink-0 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-xl font-semibold text-white shadow-[0_10px_24px_-8px_rgba(27,143,234,0.5)]">
          {initials(guest.name) || "؟"}
        </div>
        <div className="min-w-0 flex-1 space-y-1.5">
          <h1 className="truncate font-heading text-2xl font-semibold text-[#161616]">
            {guest.name}
          </h1>
          {guest.job_title || guest.company ? (
            <p className="flex items-center gap-1.5 text-sm text-[#5F6368]">
              <Briefcase className="size-3.5 shrink-0" aria-hidden="true" />
              {[guest.job_title, guest.company].filter(Boolean).join(" · ")}
            </p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
