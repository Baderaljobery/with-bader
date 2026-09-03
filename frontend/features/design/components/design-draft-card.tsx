"use client";

import { Pencil, Trash2 } from "lucide-react";
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
import { formatDate } from "@/lib/format-date";
import { cn } from "@/lib/utils";
import { useDeleteDesign } from "../hooks/use-delete-design";
import { PLATFORM_LABELS, STATUS_LABELS } from "../lib/labels";
import { getDesignTemplateById } from "../templates/registry";
import type { DesignDraft } from "../types/design";

type DesignDraftCardProps = {
  guestId: string;
  design: DesignDraft;
  onOpen: (design: DesignDraft) => void;
};

export function DesignDraftCard({ guestId, design, onOpen }: DesignDraftCardProps) {
  const deleteDesign = useDeleteDesign(guestId);
  const [deleteOpen, setDeleteOpen] = useState(false);

  const firstSlide = design.slides[0];
  const template = getDesignTemplateById(design.template_id);

  return (
    <>
      <Card size="sm" className="overflow-hidden">
        <button
          type="button"
          onClick={() => onOpen(design)}
          className="-m-(--card-spacing) mb-(--card-spacing) block w-[calc(100%+2*var(--card-spacing))] text-start"
        >
          {firstSlide && template ? (
            <template.Renderer
              role={firstSlide.role}
              aspectRatio={design.aspect_ratio}
              headline={firstSlide.headline}
              bodyText={firstSlide.body_text}
              ctaText={firstSlide.cta_text}
              className="rounded-none"
            />
          ) : null}
        </button>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium text-foreground">
                {PLATFORM_LABELS[design.platform]}
              </span>
              <span className="rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium text-foreground">
                {template?.name ?? design.template_id}
              </span>
              <span className="rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium text-foreground">
                {design.slide_count} {design.slide_count === 1 ? "شريحة" : "شرائح"}
              </span>
            </div>
            <Badge
              variant="secondary"
              className={cn(
                "font-normal",
                design.status === "approved" && "bg-emerald-50 text-emerald-700",
              )}
            >
              {STATUS_LABELS[design.status]}
            </Badge>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border/70 pt-3">
            <p className="text-xs text-muted-foreground">آخر تحديث: {formatDate(design.updated_at)}</p>
            <div className="flex items-center gap-1.5">
              <Button type="button" variant="outline" size="sm" onClick={() => onOpen(design)}>
                <Pencil className="size-3.5" />
                فتح
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label="حذف التصميم"
                onClick={() => setDeleteOpen(true)}
              >
                <Trash2 className="size-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>حذف هذا التصميم؟</AlertDialogTitle>
            <AlertDialogDescription>سيتم حذف جميع شرائحه. لا يمكن التراجع عن هذا الإجراء.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>إلغاء</AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              disabled={deleteDesign.isPending}
              onClick={() => deleteDesign.mutate(design.id, { onSuccess: () => setDeleteOpen(false) })}
            >
              حذف
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
