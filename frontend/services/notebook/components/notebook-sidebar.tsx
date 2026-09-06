"use client";

import { Plus } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useCreateNotebook } from "../hooks/use-notebook-mutations";
import type { Notebook } from "../types/notebook";
import { NotebookList } from "./notebook-list";
import { RenameDialog } from "./rename-dialog";

type NotebookSidebarProps = {
  guestId: string;
  notebooks: Notebook[];
  activeNotebookId: string;
  activePageId: string | null;
  onSelectNotebook: (notebookId: string) => void;
  onSelectPage: (pageId: string) => void;
  onNotebookDeleted: (notebookId: string) => void;
  onPageDeleted: (pageId: string) => void;
  onNotebookCreated: (notebookId: string) => void;
};

/** Reused as both the desktop aside panel content and the mobile drawer's
 * content (see notebook-workspace.tsx) - `notebooks` is always non-empty
 * here, the zero-notebooks empty state is handled one level up. */
export function NotebookSidebar({
  guestId,
  notebooks,
  activeNotebookId,
  activePageId,
  onSelectNotebook,
  onSelectPage,
  onNotebookDeleted,
  onPageDeleted,
  onNotebookCreated,
}: NotebookSidebarProps) {
  const createNotebook = useCreateNotebook(guestId);
  const [creating, setCreating] = useState(false);

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between gap-2 px-1">
        <h2 className="text-sm font-medium text-foreground">دفاتر الضيف</h2>
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          aria-label="إنشاء دفتر"
          onClick={() => setCreating(true)}
        >
          <Plus className="size-4" />
        </Button>
      </div>

      <NotebookList
        guestId={guestId}
        notebooks={notebooks}
        activeNotebookId={activeNotebookId}
        activePageId={activePageId}
        onSelectNotebook={onSelectNotebook}
        onSelectPage={onSelectPage}
        onNotebookDeleted={onNotebookDeleted}
        onPageDeleted={onPageDeleted}
      />

      {creating ? (
        <RenameDialog
          title="إنشاء دفتر"
          label="عنوان الدفتر"
          initialValue="دفتر المقابلة"
          isPending={createNotebook.isPending}
          onCancel={() => setCreating(false)}
          onSubmit={(value) => {
            createNotebook.mutate(
              { title: value },
              {
                onSuccess: (notebook) => {
                  setCreating(false);
                  onNotebookCreated(notebook.id);
                },
              },
            );
          }}
        />
      ) : null}
    </div>
  );
}
