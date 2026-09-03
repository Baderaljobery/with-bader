"use client";

import { Menu, NotebookText } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuestNotebooks } from "../hooks/use-guest-notebooks";
import { useCreateNotebook } from "../hooks/use-notebook-mutations";
import { useNotebookPages } from "../hooks/use-notebook-pages";
import type { Notebook } from "../types/notebook";
import { NotebookEditor } from "./notebook-editor";
import { NotebookSidebar } from "./notebook-sidebar";
import { RenameDialog } from "./rename-dialog";

type NotebookWorkspaceProps = {
  guestId: string;
};

/** Selection (which notebook/page is open) lives in the URL - `?notebook=
 * <id>&page=<id>` - so a page refresh or shared link lands back on the same
 * spot (see PART 49 of the notebook task spec). No fake/default notebook
 * or page is ever created automatically - only explicit user action does. */
export function NotebookWorkspace({ guestId }: NotebookWorkspaceProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const notebooksQuery = useGuestNotebooks(guestId);
  const createNotebook = useCreateNotebook(guestId);
  const [creating, setCreating] = useState(false);

  const notebookIdFromUrl = searchParams.get("notebook");
  const pageIdFromUrl = searchParams.get("page");

  function setSelection(notebookId: string | null, pageId: string | null) {
    const params = new URLSearchParams();
    if (notebookId) params.set("notebook", notebookId);
    if (pageId) params.set("page", pageId);
    const query = params.toString();
    router.replace(query ? `?${query}` : "?", { scroll: false });
  }

  if (notebooksQuery.isPending) {
    return (
      <div className="grid gap-4 md:grid-cols-[240px_1fr]">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (notebooksQuery.isError) {
    return (
      <ErrorState
        title="تعذر تحميل الدفاتر"
        description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
        onRetry={() => notebooksQuery.refetch()}
      />
    );
  }

  const notebooks = notebooksQuery.data;

  if (notebooks.length === 0) {
    return (
      <>
        <EmptyState
          icon={NotebookText}
          title="ابدأ دفتر الضيف"
          description="أنشئ دفترًا لتنظيم الملاحظات والأسئلة والأفكار الخاصة بالمقابلة."
          action={
            <Button type="button" onClick={() => setCreating(true)}>
              إنشاء دفتر
            </Button>
          }
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
                    setSelection(notebook.id, null);
                  },
                },
              );
            }}
          />
        ) : null}
      </>
    );
  }

  const activeNotebookId =
    notebookIdFromUrl && notebooks.some((notebook) => notebook.id === notebookIdFromUrl)
      ? notebookIdFromUrl
      : notebooks[0].id;

  return (
    <NotebookWorkspaceContent
      guestId={guestId}
      notebooks={notebooks}
      activeNotebookId={activeNotebookId}
      pageIdFromUrl={pageIdFromUrl}
      onSelectionChange={setSelection}
    />
  );
}

type NotebookWorkspaceContentProps = {
  guestId: string;
  notebooks: Notebook[];
  activeNotebookId: string;
  pageIdFromUrl: string | null;
  onSelectionChange: (notebookId: string | null, pageId: string | null) => void;
};

function NotebookWorkspaceContent({
  guestId,
  notebooks,
  activeNotebookId,
  pageIdFromUrl,
  onSelectionChange,
}: NotebookWorkspaceContentProps) {
  const pagesQuery = useNotebookPages(activeNotebookId);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  function selectNotebook(notebookId: string) {
    onSelectionChange(notebookId, null);
  }

  function selectPage(pageId: string) {
    onSelectionChange(activeNotebookId, pageId);
    setMobileNavOpen(false);
  }

  function handleNotebookDeleted(deletedId: string) {
    const remaining = notebooks.filter((notebook) => notebook.id !== deletedId);
    onSelectionChange(remaining[0]?.id ?? null, null);
  }

  function handlePageDeleted(deletedId: string) {
    if (deletedId !== activePageId) return;
    const remaining = (pagesQuery.data ?? []).filter((page) => page.id !== deletedId);
    onSelectionChange(activeNotebookId, remaining[0]?.id ?? null);
  }

  if (pagesQuery.isPending) {
    return (
      <div className="grid gap-4 md:grid-cols-[240px_1fr]">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (pagesQuery.isError) {
    return (
      <ErrorState
        title="تعذر تحميل صفحات الدفتر"
        description="تأكد من أن الخادم يعمل ثم حاول مرة أخرى."
        onRetry={() => pagesQuery.refetch()}
      />
    );
  }

  const pages = pagesQuery.data;
  const activePageId =
    pageIdFromUrl && pages.some((page) => page.id === pageIdFromUrl) ? pageIdFromUrl : (pages[0]?.id ?? null);
  const activePage = pages.find((page) => page.id === activePageId) ?? null;

  const sidebarProps = {
    guestId,
    notebooks,
    activeNotebookId,
    activePageId,
    onSelectNotebook: selectNotebook,
    onSelectPage: selectPage,
    onNotebookDeleted: handleNotebookDeleted,
    onPageDeleted: handlePageDeleted,
    onNotebookCreated: (notebookId: string) => onSelectionChange(notebookId, null),
  };

  return (
    <div className="grid gap-5 md:grid-cols-[260px_1fr]">
      <div className="hidden md:block">
        <div className="rounded-2xl border border-border bg-white p-2.5 shadow-[var(--shadow-soft)]">
          <NotebookSidebar {...sidebarProps} />
        </div>
      </div>

      <div className="md:hidden">
        <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
          <SheetTrigger render={<Button type="button" variant="outline" size="sm" />}>
            <Menu className="size-4" />
            الدفاتر والصفحات
          </SheetTrigger>
          <SheetContent side="right" className="w-80 max-w-[85vw] p-0">
            <SheetHeader className="border-b border-border">
              <SheetTitle>الدفاتر والصفحات</SheetTitle>
            </SheetHeader>
            <div className="flex-1 overflow-y-auto p-3">
              <NotebookSidebar {...sidebarProps} />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      <div className="relative min-w-0 overflow-hidden rounded-3xl border border-border bg-white p-5 shadow-[var(--shadow-soft)] md:p-8">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-24 end-[-6rem] size-72 rounded-full opacity-50 blur-3xl"
          style={{ backgroundImage: "var(--glow-teal)" }}
        />
        <div className="relative">
          <NotebookEditor
            page={activePage}
            notebookId={activeNotebookId}
            guestId={guestId}
            onPageDeleted={handlePageDeleted}
          />
        </div>
      </div>
    </div>
  );
}
