"use client";

import { useState } from "react";

import { PageHeader } from "@/components/shared/page-header";
import { GuestFormDialog } from "@/features/guests/components/guest-form-dialog";
import { GuestGrid } from "@/features/guests/components/guest-grid";

export default function HomePage() {
  const [addOpen, setAddOpen] = useState(false);

  return (
    <div className="space-y-6">
      <PageHeader
        title="مرحبًا بدر 👋"
        description="إدارة الضيوف والمقابلات في مكان واحد."
      />

      <GuestGrid onAddGuest={() => setAddOpen(true)} />

      <GuestFormDialog open={addOpen} onOpenChange={setAddOpen} />
    </div>
  );
}
