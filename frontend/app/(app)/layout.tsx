import type { ReactNode } from "react";

import { AppShell } from "@/components/app-shell/app-shell";
import { AuthGuard } from "@/services/auth/components/auth-guard";

export default function AppGroupLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <AppShell>{children}</AppShell>
    </AuthGuard>
  );
}
