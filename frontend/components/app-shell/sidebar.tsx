import { Brand } from "./brand";
import { SidebarNav } from "./sidebar-nav";
import { SidebarUser } from "./sidebar-user";

/**
 * Desktop right sidebar. Always the LAST child of the (dir="ltr") shell row
 * in app-shell.tsx, so it renders on the physical right regardless of the
 * content area's text direction - see app-shell.tsx for why. That outer
 * dir="ltr" only controls the sidebar's own position among its siblings,
 * though - left unchecked it would also leak into everything *inside* the
 * sidebar (nav icon/label order, text alignment), which must stay RTL like
 * the rest of the app. `dir="rtl"` here re-establishes that for its
 * contents without moving the <aside> itself.
 */
export function Sidebar() {
  return (
    <aside dir="rtl" className="hidden w-72 shrink-0 flex-col border-l border-[#E6EAF0] bg-white px-4 py-6 md:flex">
      <div className="relative overflow-hidden rounded-2xl border border-[#E6EAF0] bg-secondary/50 px-4 py-5">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-14 start-1/2 size-44 -translate-x-1/2 rounded-full opacity-90 blur-2xl"
          style={{ backgroundImage: "var(--glow-teal)" }}
        />
        <div className="relative flex justify-center">
          <Brand size="nav" className="px-0" />
        </div>
      </div>
      <div className="mt-4 flex-1">
        <SidebarNav />
      </div>
      <div className="border-t border-[#E6EAF0] pt-4">
        <SidebarUser />
      </div>
    </aside>
  );
}
