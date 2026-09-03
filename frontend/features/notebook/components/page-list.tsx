"use client";

import { MoreVertical, Pencil, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { useNotebookPages } from "../hooks/use-notebook-pages";
import { useCreatePage, useDeletePage, useRenamePage } from "../hooks/use-page-mutations";
import { nextPagePosition } from "../lib/position";
import type { NotebookPage } from "../types/notebook-page";
import { DeleteConfirmDialog } from "./delete-confirm-dialog";
import { RenameDialog } from "./rename-dialog";

type PageListProps = {
  notebookId: string;
  activePageId: string | null;
  onSelectPage: (pageId: string) => void;
  onPageDeleted?: (pageId: string) => void;
};

export function PageList({ notebookId, activePageId, onSelectPage, onPageDeleted }: PageListProps) {
  const pagesQuery = useNotebookPages(notebookId);
  const renamePage = useRenamePage(notebookId);
  const deletePage = useDeletePage(notebookId);
  const createPage = useCreatePage(notebookId);
  const [renamingPage, setRenamingPage] = useState<NotebookPage | null>(null);
  const [deletingPage, setDeletingPage] = useState<NotebookPage | null>(null);
  const [creatingPage, setCreatingPage] = useState(false);

  if (pagesQuery.isPending) {
    return (
      <div className="space-y-1 py-1">
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-6 w-full" />
      </div>
    );
  }

  if (pagesQuery.isError) {
    return <p className="px-1.5 py-1 text-xs text-destructive">تعذر تحميل الصفحات</p>;
  }

  const pages = pagesQuery.data;

  return (
    <div className="space-y-0.5">
      {pages.length === 0 ? (
        <p className="px-1.5 py-1 text-xs text-muted-foreground">لا توجد صفحات بعد</p>
      ) : (
        pages.map((page) => {
          const isActive = page.id === activePageId;
          return (
            <div
              key={page.id}
              className={cn(
                "group/page flex items-center gap-1 rounded-md px-1.5 py-1 text-sm",
                isActive
                  ? "bg-background font-medium text-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-secondary/60",
              )}
            >
              <button
                type="button"
                onClick={() => onSelectPage(page.id)}
                className="min-w-0 flex-1 truncate text-start"
              >
                {page.title}
              </button>
              <DropdownMenu>
                <DropdownMenuTrigger
                  render={
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-xs"
                      className="opacity-0 group-hover/page:opacity-100"
                      aria-label="خيارات الصفحة"
                    />
                  }
                >
                  <MoreVertical className="size-3" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  <DropdownMenuItem onClick={() => setRenamingPage(page)}>
                    <Pencil className="size-3.5" />
                    إعادة تسمية
                  </DropdownMenuItem>
                  <DropdownMenuItem variant="destructive" onClick={() => setDeletingPage(page)}>
                    <Trash2 className="size-3.5" />
                    حذف
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          );
        })
      )}

      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-6 w-full justify-start px-1.5 text-xs text-muted-foreground"
        onClick={() => setCreatingPage(true)}
      >
        <Plus className="size-3" aria-hidden="true" />
        صفحة جديدة
      </Button>

      {creatingPage ? (
        <RenameDialog
          title="صفحة جديدة"
          label="عنوان الصفحة"
          initialValue="صفحة جديدة"
          isPending={createPage.isPending}
          onCancel={() => setCreatingPage(false)}
          onSubmit={(value) => {
            createPage.mutate(
              { title: value, position: nextPagePosition(pages) },
              {
                onSuccess: (page) => {
                  setCreatingPage(false);
                  onSelectPage(page.id);
                },
              },
            );
          }}
        />
      ) : null}

      {renamingPage ? (
        <RenameDialog
          title="إعادة تسمية الصفحة"
          label="عنوان الصفحة"
          initialValue={renamingPage.title}
          isPending={renamePage.isPending}
          onCancel={() => setRenamingPage(null)}
          onSubmit={(value) => {
            renamePage.mutate(
              { pageId: renamingPage.id, input: { title: value } },
              { onSuccess: () => setRenamingPage(null) },
            );
          }}
        />
      ) : null}

      {deletingPage ? (
        <DeleteConfirmDialog
          title="حذف الصفحة؟"
          description={`سيتم حذف "${deletingPage.title}" وجميع الكتل الموجودة بداخلها نهائيًا. لا يمكن التراجع عن هذا الإجراء.`}
          confirmLabel="حذف الصفحة"
          isPending={deletePage.isPending}
          onCancel={() => setDeletingPage(null)}
          onConfirm={() => {
            deletePage.mutate(deletingPage.id, {
              onSuccess: () => {
                onPageDeleted?.(deletingPage.id);
                setDeletingPage(null);
              },
            });
          }}
        />
      ) : null}
    </div>
  );
}
