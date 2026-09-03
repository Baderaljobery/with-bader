"use client";

import { useIsMutating } from "@tanstack/react-query";
import { Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BLOCK_CONTENT_SAVE_MUTATION_KEY } from "../hooks/use-block-mutations";
import { useDeletePage, useRenamePage } from "../hooks/use-page-mutations";
import type { NotebookPage } from "../types/notebook-page";

type PageHeaderProps = {
  page: NotebookPage;
  notebookId: string;
  onDeleted: () => void;
};

export function PageHeader({ page, notebookId, onDeleted }: PageHeaderProps) {
  const renamePage = useRenamePage(notebookId);
  const deletePage = useDeletePage(notebookId);

  const [title, setTitle] = useState(page.title);
  const [lastPageId, setLastPageId] = useState(page.id);
  const [deleteOpen, setDeleteOpen] = useState(false);

  // Adjust the local draft during render when switching pages - never in a
  // useEffect, which would race an in-progress keystroke on the page being
  // left.
  if (page.id !== lastPageId) {
    setLastPageId(page.id);
    setTitle(page.title);
  }

  const isMutating = useIsMutating({ mutationKey: [BLOCK_CONTENT_SAVE_MUTATION_KEY, page.id] });
  const [previousIsMutating, setPreviousIsMutating] = useState(isMutating);
  const [justSaved, setJustSaved] = useState(false);

  // Detect the "was saving, now idle" transition during render (state
  // only, no refs - see use-local-draft.ts for why) and flip justSaved on;
  // the timer that flips it back off lives in the effect below, where an
  // async setState (inside setTimeout) is the correct place for it.
  if (isMutating !== previousIsMutating) {
    setPreviousIsMutating(isMutating);
    if (isMutating > 0) {
      setJustSaved(false);
    } else if (previousIsMutating > 0) {
      setJustSaved(true);
    }
  }

  useEffect(() => {
    if (!justSaved) return;
    const timeout = setTimeout(() => setJustSaved(false), 2000);
    return () => clearTimeout(timeout);
  }, [justSaved]);

  function commitTitle() {
    const trimmed = title.trim();
    if (!trimmed || trimmed === page.title) {
      setTitle(page.title);
      return;
    }
    renamePage.mutate({ pageId: page.id, input: { title: trimmed } });
  }

  function handleDelete() {
    deletePage.mutate(page.id, { onSuccess: onDeleted });
  }

  return (
    <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border pb-3">
      <Input
        value={title}
        onChange={(event) => setTitle(event.target.value)}
        onBlur={commitTitle}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.currentTarget.blur();
          }
        }}
        aria-label="عنوان الصفحة"
        className="h-auto flex-1 border-none bg-transparent px-0 font-heading text-xl font-semibold text-foreground shadow-none focus-visible:ring-0"
      />

      <div className="flex items-center gap-2 pt-1.5">
        {isMutating > 0 ? (
          <span className="text-xs text-muted-foreground">جارٍ الحفظ...</span>
        ) : justSaved ? (
          <span className="text-xs text-muted-foreground">تم الحفظ</span>
        ) : null}

        <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
          <AlertDialogTrigger
            render={
              <Button type="button" variant="ghost" size="icon-sm" aria-label="حذف الصفحة" />
            }
          >
            <Trash2 className="size-4" />
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>حذف الصفحة؟</AlertDialogTitle>
              <AlertDialogDescription>
                سيتم حذف &quot;{page.title}&quot; وجميع الكتل الموجودة بداخلها نهائيًا. لا يمكن
                التراجع عن هذا الإجراء.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>إلغاء</AlertDialogCancel>
              <AlertDialogAction variant="destructive" onClick={handleDelete}>
                حذف الصفحة
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
