"use client";

import { MoreVertical, Palette, Pencil, ShieldCheck, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { formatDate } from "@/lib/format-date";
import { cn } from "@/lib/utils";
import { useApproveContent } from "../hooks/use-approve-content";
import { useDeleteContent } from "../hooks/use-delete-content";
import { LENGTH_LABELS, PLATFORM_ICONS, PLATFORM_LABELS, STATUS_LABELS } from "../lib/labels";
import type { ContentDraft } from "../types/content";

type ContentDraftCardProps = {
  guestId: string;
  draft: ContentDraft;
  onOpen: (draft: ContentDraft) => void;
};

export function ContentDraftCard({ guestId, draft, onOpen }: ContentDraftCardProps) {
  const router = useRouter();
  const approveContent = useApproveContent(guestId);
  const deleteContent = useDeleteContent(guestId);
  const [deleteOpen, setDeleteOpen] = useState(false);

  const Icon = PLATFORM_ICONS[draft.platform];

  return (
    <>
      <Card>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-secondary text-[#1B8FEA]">
                <Icon className="size-4" aria-hidden="true" />
              </span>
              <div>
                <p className="text-sm font-medium text-foreground">{PLATFORM_LABELS[draft.platform]}</p>
                <p className="text-xs text-muted-foreground">{LENGTH_LABELS[draft.length]}</p>
              </div>
            </div>
            <Badge
              variant="secondary"
              className={cn(
                "font-normal",
                draft.status === "approved" && "bg-emerald-50 text-emerald-700",
              )}
            >
              {STATUS_LABELS[draft.status]}
            </Badge>
          </div>

          <p className="line-clamp-3 text-sm leading-6 text-foreground">{draft.content}</p>

          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border/70 pt-3">
            <p className="text-xs text-muted-foreground">آخر تحديث: {formatDate(draft.updated_at)}</p>
            <div className="flex items-center gap-1.5">
              <Button type="button" variant="outline" size="sm" onClick={() => onOpen(draft)}>
                <Pencil className="size-3.5" />
                فتح
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger
                  render={
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-sm"
                      aria-label="خيارات المحتوى"
                    />
                  }
                >
                  <MoreVertical className="size-4" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {draft.status !== "approved" ? (
                    <DropdownMenuItem onClick={() => approveContent.mutate(draft.id)}>
                      <ShieldCheck className="size-4" />
                      اعتماد
                    </DropdownMenuItem>
                  ) : null}
                  <DropdownMenuItem
                    onClick={() => router.push(`/guests/${guestId}/design?content=${draft.id}`)}
                  >
                    <Palette className="size-4" />
                    إرسال إلى التصميم
                  </DropdownMenuItem>
                  <DropdownMenuItem variant="destructive" onClick={() => setDeleteOpen(true)}>
                    <Trash2 className="size-4" />
                    حذف
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardContent>
      </Card>

      <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>حذف هذا المحتوى؟</AlertDialogTitle>
            <AlertDialogDescription>لا يمكن التراجع عن هذا الإجراء.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>إلغاء</AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              disabled={deleteContent.isPending}
              onClick={() => deleteContent.mutate(draft.id, { onSuccess: () => setDeleteOpen(false) })}
            >
              حذف
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
