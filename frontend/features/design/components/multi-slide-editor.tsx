"use client";

import { AlertTriangle, Download, Trash2, X } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";

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
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useDeleteDesign } from "../hooks/use-delete-design";
import { useUpdateSlide } from "../hooks/use-update-slide";
import { PLATFORM_LABELS, SLIDE_ROLE_LABELS, STATUS_LABELS } from "../lib/labels";
import { evaluateContentFit } from "../templates/content-fit";
import { downloadBlob, exportSlideToPng } from "../templates/export";
import { getDesignTemplateById } from "../templates/registry";
import type { DesignDraft, DesignSlide } from "../types/design";

type MultiSlideEditorProps = {
  guestId: string;
  design: DesignDraft;
  onBack: () => void;
  onDeleted: () => void;
};

/** The strict template-renderer flow (Part 16/30): no "regenerate image"
 * controls here at all - the template is deterministic frontend code, so
 * editing text is the only thing that changes what renders, and it updates
 * instantly with no AI call. What used to be a Gemini regenerate button is
 * now a real PNG export (Part 32-34). */
export function MultiSlideEditor({ guestId, design, onBack, onDeleted }: MultiSlideEditorProps) {
  const [current, setCurrent] = useState(design);
  const [activeIndex, setActiveIndex] = useState(design.slides[0]?.slide_index ?? 1);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [exportingAll, setExportingAll] = useState(false);

  const updateSlide = useUpdateSlide(guestId);
  const deleteDesign = useDeleteDesign(guestId);

  const template = getDesignTemplateById(current.template_id);
  const activeSlide = current.slides.find((s) => s.slide_index === activeIndex) ?? current.slides[0];

  const [headline, setHeadline] = useState(activeSlide?.headline ?? "");
  const [bodyText, setBodyText] = useState(activeSlide?.body_text ?? "");
  const [ctaText, setCtaText] = useState(activeSlide?.cta_text ?? "");

  const mainRef = useRef<HTMLDivElement>(null);
  const thumbRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  function switchSlide(slide: DesignSlide) {
    setActiveIndex(slide.slide_index);
    setHeadline(slide.headline);
    setBodyText(slide.body_text);
    setCtaText(slide.cta_text ?? "");
  }

  function patchSlideInDraft(slide: DesignSlide) {
    setCurrent((prev) => ({
      ...prev,
      slides: prev.slides.map((s) => (s.slide_index === slide.slide_index ? slide : s)),
    }));
  }

  function handleSaveText() {
    if (!activeSlide) return;
    updateSlide.mutate(
      {
        designId: current.id,
        slideIndex: activeSlide.slide_index,
        input: { headline, body_text: bodyText, cta_text: ctaText.trim() || null },
      },
      { onSuccess: (slide) => patchSlideInDraft(slide) },
    );
  }

  async function handleExportActive() {
    if (!mainRef.current) return;
    try {
      const blob = await exportSlideToPng(mainRef.current, current.aspect_ratio);
      downloadBlob(blob, `${current.template_id}-slide-${activeIndex}.png`);
    } catch {
      toast.error("تعذّر تصدير الشريحة كصورة");
    }
  }

  async function handleExportAll() {
    setExportingAll(true);
    try {
      for (const slide of current.slides) {
        const node = current.slides.length > 1 ? thumbRefs.current.get(slide.slide_index) : mainRef.current;
        if (!node) continue;
        const blob = await exportSlideToPng(node, current.aspect_ratio);
        downloadBlob(blob, `${current.template_id}-slide-${slide.slide_index}.png`);
        // Space downloads out slightly - triggering several in the same tick
        // makes some browsers silently drop all but the first.
        await new Promise((resolve) => setTimeout(resolve, 250));
      }
    } catch {
      toast.error("تعذّر تصدير كل الشرائح");
    } finally {
      setExportingAll(false);
    }
  }

  const dirty =
    !!activeSlide &&
    (headline !== activeSlide.headline || bodyText !== activeSlide.body_text || ctaText !== (activeSlide.cta_text ?? ""));

  if (!activeSlide || !template) {
    return null;
  }

  const limits = template.contentLimits[activeSlide.role];
  const fit = evaluateContentFit(limits, headline, bodyText);

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-foreground">
            {PLATFORM_LABELS[current.platform]}
          </span>
          <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-foreground">
            {template.name}
          </span>
          {current.status === "approved" ? (
            <Badge className="border-0 bg-emerald-50 font-normal text-emerald-700">
              {STATUS_LABELS.approved}
            </Badge>
          ) : null}
        </div>
        <Button type="button" variant="ghost" size="icon-sm" aria-label="رجوع" onClick={onBack}>
          <X className="size-4" />
        </Button>
      </div>

      {current.slides.length > 1 ? (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {current.slides.map((slide) => (
            <button
              key={slide.id}
              type="button"
              onClick={() => switchSlide(slide)}
              className={cn(
                "w-24 shrink-0 overflow-hidden rounded-xl border-2 transition-all",
                slide.slide_index === activeIndex ? "border-[#1B8FEA]" : "border-transparent opacity-70 hover:opacity-100",
              )}
            >
              <template.Renderer
                ref={(el) => {
                  if (el) thumbRefs.current.set(slide.slide_index, el);
                  else thumbRefs.current.delete(slide.slide_index);
                }}
                role={slide.role}
                aspectRatio={current.aspect_ratio}
                headline={slide.headline}
                bodyText={slide.body_text}
                ctaText={slide.cta_text}
              />
            </button>
          ))}
        </div>
      ) : null}

      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-muted-foreground">
          الشريحة {activeIndex} من {current.slide_count}
        </span>
        <Badge variant="secondary" className="font-normal">
          {SLIDE_ROLE_LABELS[activeSlide.role]}
        </Badge>
      </div>

      <div className="mx-auto w-full max-w-sm">
        <template.Renderer
          ref={mainRef}
          role={activeSlide.role}
          aspectRatio={current.aspect_ratio}
          headline={headline}
          bodyText={bodyText}
          ctaText={ctaText}
        />
      </div>

      <div className="space-y-3">
        <Input
          value={headline}
          onChange={(event) => setHeadline(event.target.value)}
          placeholder="العنوان الرئيسي"
          className="font-heading text-base font-medium"
          aria-label="العنوان الرئيسي"
        />
        <Textarea
          value={bodyText}
          onChange={(event) => setBodyText(event.target.value)}
          rows={activeSlide.role === "quick_points" ? 5 : 4}
          placeholder={activeSlide.role === "quick_points" ? "نقطة في كل سطر" : "نص الشريحة"}
          aria-label="نص الشريحة"
        />
        <Input
          value={ctaText}
          onChange={(event) => setCtaText(event.target.value)}
          placeholder="نص دعوة أو تذييل صغير (اختياري)"
          aria-label="نص الدعوة أو التذييل"
        />
        {!fit.fits ? (
          <div className="flex items-start gap-1.5 text-xs text-amber-700">
            <AlertTriangle className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
            <span>{fit.reasons.join(" - ")}</span>
          </div>
        ) : null}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" onClick={handleSaveText} disabled={!dirty || updateSlide.isPending}>
          حفظ نص الشريحة
        </Button>
        <Button type="button" variant="outline" onClick={handleExportActive}>
          <Download className="size-4" />
          تنزيل هذه الشريحة (PNG)
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-2 border-t border-border/70 pt-4">
        {current.slides.length > 1 ? (
          <Button type="button" variant="outline" onClick={handleExportAll} disabled={exportingAll}>
            <Download className="size-4" />
            {exportingAll ? "جارٍ تنزيل الشرائح..." : "تنزيل جميع الشرائح (PNG)"}
          </Button>
        ) : null}
        <Button
          type="button"
          variant="outline"
          className="text-destructive hover:text-destructive"
          onClick={() => setDeleteOpen(true)}
        >
          <Trash2 className="size-4" />
          حذف التصميم
        </Button>
      </div>

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
              onClick={() =>
                deleteDesign.mutate(current.id, {
                  onSuccess: () => {
                    setDeleteOpen(false);
                    onDeleted();
                  },
                })
              }
            >
              حذف
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
