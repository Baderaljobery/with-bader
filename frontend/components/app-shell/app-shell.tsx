import type { ReactNode } from "react";

import { AmbientBackground } from "@/components/shared/ambient-background";
import { MobileTopbar } from "./mobile-topbar";
import { Sidebar } from "./sidebar";

/**
 * The shell's own row direction is pinned to ltr so the sidebar stays on
 * the physical right edge no matter what language/direction the product
 * supports later - only the content area's direction should ever change.
 * See sidebar.tsx.
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div dir="ltr" className="flex h-dvh min-h-dvh w-full overflow-hidden bg-[#FAFBFD]">
      <div dir="rtl" className="relative flex min-w-0 flex-1 flex-col">
        <AmbientBackground />
        <MobileTopbar />
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
            {children}
          </div>
        </main>
      </div>
      <Sidebar />
    </div>
  );
}
