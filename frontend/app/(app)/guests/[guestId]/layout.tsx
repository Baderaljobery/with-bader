import { GuestWorkspaceShell } from "@/features/guests/components/guest-workspace-shell";

export default function GuestWorkspaceLayout({ children }: LayoutProps<"/guests/[guestId]">) {
  return <GuestWorkspaceShell>{children}</GuestWorkspaceShell>;
}
