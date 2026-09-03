"use client";

import { ChevronDown, ChevronLeft, MoreVertical, Pencil, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useDeleteNotebook, useRenameNotebook } from "../hooks/use-notebook-mutations";
import type { Notebook } from "../types/notebook";
import { DeleteConfirmDialog } from "./delete-confirm-dialog";
import { PageList } from "./page-list";
import { RenameDialog } from "./rename-dialog";

type NotebookListProps = {
  guestId: string;
  notebooks: Notebook[];
  activeNotebookId: string | null;
  activePageId: string | null;
  onSelectNotebook: (notebookId: string) => void;
  onSelectPage: (pageId: string) => void;
  onNotebookDeleted: (notebookId: string) => void;
  onPageDeleted: (pageId: string) => void;
};

export function NotebookList({
  guestId,
  notebooks,
  activeNotebookId,
  activePageId,
  onSelectNotebook,
  onSelectPage,
  onNotebookDeleted,
  onPageDeleted,
}: NotebookListProps) {
  const renameNotebook = useRenameNotebook(guestId);
  const deleteNotebook = useDeleteNotebook(guestId);
  const [renamingNotebook, setRenamingNotebook] = useState<Notebook | null>(null);
  const [deletingNotebook, setDeletingNotebook] = useState<Notebook | null>(null);

  return (
    <div className="space-y-1">
      {notebooks.map((notebook) => {
        const isActive = notebook.id === activeNotebookId;
        return (
          <div key={notebook.id}>
            <div
              className={cn(
                "group/notebook flex items-center gap-1 rounded-lg px-2 py-1.5 text-sm",
                isActive
                  ? "bg-secondary font-medium text-foreground"
                  : "text-muted-foreground hover:bg-secondary/60",
              )}
            >
              <button
                type="button"
                onClick={() => onSelectNotebook(notebook.id)}
                className="flex min-w-0 flex-1 items-center gap-1.5 text-start"
              >
                {isActive ? (
                  <ChevronDown className="size-3.5 shrink-0" aria-hidden="true" />
                ) : (
                  <ChevronLeft className="size-3.5 shrink-0 rtl:rotate-180" aria-hidden="true" />
                )}
                <span className="truncate">{notebook.title}</span>
              </button>

              <DropdownMenu>
                <DropdownMenuTrigger
                  render={
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-xs"
                      className="opacity-0 group-hover/notebook:opacity-100"
                      aria-label="خيارات الدفتر"
                    />
                  }
                >
                  <MoreVertical className="size-3.5" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  <DropdownMenuItem onClick={() => setRenamingNotebook(notebook)}>
                    <Pencil className="size-3.5" />
                    إعادة تسمية
                  </DropdownMenuItem>
                  <DropdownMenuItem variant="destructive" onClick={() => setDeletingNotebook(notebook)}>
                    <Trash2 className="size-3.5" />
                    حذف
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {isActive ? (
              <div className="mt-0.5 ms-4 space-y-0.5 border-s border-border ps-2">
                <PageList
                  notebookId={notebook.id}
                  activePageId={activePageId}
                  onSelectPage={onSelectPage}
                  onPageDeleted={onPageDeleted}
                />
              </div>
            ) : null}
          </div>
        );
      })}

      {renamingNotebook ? (
        <RenameDialog
          title="إعادة تسمية الدفتر"
          label="عنوان الدفتر"
          initialValue={renamingNotebook.title}
          isPending={renameNotebook.isPending}
          onCancel={() => setRenamingNotebook(null)}
          onSubmit={(value) => {
            renameNotebook.mutate(
              { notebookId: renamingNotebook.id, input: { title: value } },
              { onSuccess: () => setRenamingNotebook(null) },
            );
          }}
        />
      ) : null}

      {deletingNotebook ? (
        <DeleteConfirmDialog
          title="حذف الدفتر؟"
          description={`سيتم حذف دفتر "${deletingNotebook.title}" وجميع صفحاته وكتله نهائيًا. لا يمكن التراجع عن هذا الإجراء.`}
          confirmLabel="حذف الدفتر"
          isPending={deleteNotebook.isPending}
          onCancel={() => setDeletingNotebook(null)}
          onConfirm={() => {
            deleteNotebook.mutate(deletingNotebook.id, {
              onSuccess: () => {
                onNotebookDeleted(deletingNotebook.id);
                setDeletingNotebook(null);
              },
            });
          }}
        />
      ) : null}
    </div>
  );
}
