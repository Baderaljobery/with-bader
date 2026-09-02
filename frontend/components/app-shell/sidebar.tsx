import { Brand } from "./brand";
import { SidebarNav } from "./sidebar-nav";

/**
 * Desktop right sidebar. Always the LAST child of the (dir="ltr") shell row
 * in app-shell.tsx, so it renders on the physical right regardless of the
 * content area's text direction - see app-shell.tsx for why.
 */
export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-l border-[#E6EAF0] bg-white px-4 py-6 md:flex">
      <div className="border-b border-[#E6EAF0] pb-6">
        <Brand size="nav" className="px-3" />
      </div>
      <div className="mt-6 flex-1">
        <SidebarNav />
      </div>
    </aside>
  );
}
