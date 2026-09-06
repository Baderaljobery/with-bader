import { FileText } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { BlockEditor } from "./block-editor";
import { PageHeader } from "./page-header";
import type { NotebookPage } from "../types/notebook-page";

type NotebookEditorProps = {
  page: NotebookPage | null;
  notebookId: string;
  guestId: string;
  onPageDeleted: (pageId: string) => void;
};

export function NotebookEditor({ page, notebookId, guestId, onPageDeleted }: NotebookEditorProps) {
  if (!page) {
    return (
      <EmptyState
        icon={FileText}
        title="اختر صفحة أو أنشئ صفحة جديدة"
        description="اختر صفحة من القائمة، أو أنشئ صفحة جديدة لبدء الكتابة."
      />
    );
  }

  return (
    <div className="mx-auto w-full max-w-[860px] space-y-4">
      <PageHeader page={page} notebookId={notebookId} onDeleted={() => onPageDeleted(page.id)} />
      <BlockEditor pageId={page.id} guestId={guestId} />
    </div>
  );
}
