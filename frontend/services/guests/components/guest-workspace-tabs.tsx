"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

type WorkspaceTab = {
  label: string;
  segment: string | null;
};

const WORKSPACE_TABS: WorkspaceTab[] = [
  { label: "نظرة عامة", segment: null },
  { label: "البحث", segment: "research" },
  { label: "الأسئلة", segment: "questions" },
  { label: "المقابلة", segment: "interview" },
  { label: "الدفتر", segment: "notebook" },
  { label: "المحتوى", segment: "content" },
  { label: "التصميم", segment: "design" },
];

export function GuestWorkspaceTabs({ guestId }: { guestId: string }) {
  const pathname = usePathname();
  const basePath = `/guests/${guestId}`;

  return (
    <nav
      aria-label="أقسام مساحة عمل الضيف"
      className="flex gap-1 overflow-x-auto rounded-2xl border border-border bg-secondary/40 p-1.5"
    >
      {WORKSPACE_TABS.map((tab) => {
        const href = tab.segment ? `${basePath}/${tab.segment}` : basePath;
        const active = pathname === href;

        return (
          <Link
            key={tab.label}
            href={href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "shrink-0 rounded-xl px-4 py-2 text-sm font-medium transition-all",
              active
                ? "bg-[image:var(--gradient-primary)] text-white shadow-[0_10px_24px_-10px_rgba(27,143,234,0.55)]"
                : "text-[#5F6368] hover:bg-white/70 hover:text-[#161616]",
            )}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
