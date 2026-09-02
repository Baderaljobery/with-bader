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
      className="-mx-1 flex gap-1 overflow-x-auto border-b border-[#E6EAF0] px-1"
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
              "shrink-0 border-b-2 px-3 py-2.5 text-sm font-medium transition-colors",
              active
                ? "border-[#1B8FEA] text-[#161616]"
                : "border-transparent text-[#5F6368] hover:text-[#161616]",
            )}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
