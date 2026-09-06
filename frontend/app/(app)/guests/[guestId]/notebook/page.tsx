"use client";

import { useParams } from "next/navigation";
import { Suspense } from "react";

import { NotebookWorkspace } from "@/services/notebook/components/notebook-workspace";

export default function GuestNotebookPage() {
  const { guestId } = useParams<{ guestId: string }>();

  return (
    <Suspense fallback={null}>
      <NotebookWorkspace guestId={guestId} />
    </Suspense>
  );
}
