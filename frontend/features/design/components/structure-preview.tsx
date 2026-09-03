"use client";

import { AlertTriangle, Check } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useCreateDesign } from "../hooks/use-create-design";
import { SLIDE_ROLE_LABELS } from "../lib/labels";
import { evaluateContentFit } from "../templates/content-fit";
import { getDesignTemplateById } from "../templates/registry";
import type { DesignConfig } from "./configuration-form";
import { GenerationLoadingState } from "./generation-loading-state";
import type { DesignDraft, DesignPlanResponse, DesignSlideInput, PlannedSlide } from "../types/design";

type StructurePreviewProps = {
  guestId: string;
  plan: DesignPlanResponse;
  config: DesignConfig;
  onBack: () => void;
  onGenerated: (draft: DesignDraft) => void;
};

/** Part 29: Configuration -> AI content plan -> text structure preview ->
 * user edits -> create/save design -> template renderer preview. No image
 * generation happens anywhere in this step (or anywhere in the normal
 * flow) - "إنشاء التصاميم" below only persists the approved text; the very
 * next screen is the real deterministic template renderer, not a
 * generation wait. The live preview here already uses that same real
 * renderer (Part 14), so what the user edits here is exactly what ships. */
export function StructurePreview({ guestId, plan, config, onBack, onGenerated }: StructurePreviewProps) {
  const createDesign = useCreateDesign(guestId);
  const template = getDesignTemplateById(config.templateId);

  const [slides, setSlides] = useState<PlannedSlide[]>(plan.slides);

  function updateSlide(index: number, patch: Partial<PlannedSlide>) {
    setSlides((current) => current.map((slide) => (slide.index === index ? { ...slide, ...patch } : slide)));
  }

  async function handleCreate() {
    const input: DesignSlideInput[] = slides.map((slide) => ({
      index: slide.index,
      role: slide.role,
      headline: slide.headline,
      body_text: slide.body_text,
      cta_text: slide.cta_text,
    }));

    const draft = await createDesign.mutateAsync({
      content_draft_id: config.contentDraftId,
      question_ids: config.questionIds,
      notebook_block_ids: config.notebookBlockIds,
      template_id: config.templateId,
      slide_count: config.slideCount,
      slides: input,
      platform: config.platform,
      aspect_ratio: config.aspectRatio,
      custom_instructions: config.customInstructions.trim() || null,
    });

    onGenerated(draft);
  }

  const canSubmit = slides.every((slide) => slide.headline.trim().length > 0) && !createDesign.isPending;

  if (createDesign.isPending) {
    return <GenerationLoadingState message="جارٍ حفظ الشرائح..." />;
  }

  return (
    <div className="space-y-6">
      <div className="space-y-5">
        {slides.map((slide) => {
          const limits = template?.contentLimits[slide.role];
          const fit = limits ? evaluateContentFit(limits, slide.headline, slide.body_text) : { fits: true, reasons: [] };

          return (
            <div key={slide.index} className="grid grid-cols-1 gap-4 rounded-2xl border border-border bg-white p-4 sm:grid-cols-[minmax(0,1fr)_160px]">
              <div className="space-y-2.5">
                <div className="flex items-center gap-2">
                  <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-secondary text-xs font-semibold text-foreground">
                    {slide.index}
                  </span>
                  <Badge variant="secondary" className="font-normal">
                    {SLIDE_ROLE_LABELS[slide.role]}
                  </Badge>
                </div>
                <Input
                  value={slide.headline}
                  onChange={(event) => updateSlide(slide.index, { headline: event.target.value })}
                  placeholder="العنوان الرئيسي"
                  className="font-heading text-sm font-medium"
                  aria-label={`عنوان الشريحة ${slide.index}`}
                />
                <Textarea
                  value={slide.body_text}
                  onChange={(event) => updateSlide(slide.index, { body_text: event.target.value })}
                  placeholder={slide.role === "quick_points" ? "نقطة في كل سطر" : "نص الشريحة"}
                  rows={slide.role === "quick_points" ? 4 : 3}
                  aria-label={`نص الشريحة ${slide.index}`}
                />
                {!fit.fits ? (
                  <div className="flex items-start gap-1.5 text-xs text-amber-700">
                    <AlertTriangle className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
                    <span>{fit.reasons.join(" - ")}</span>
                  </div>
                ) : null}
              </div>

              <div className="mx-auto w-full max-w-40 sm:mx-0">
                {template ? (
                  <template.Renderer
                    role={slide.role}
                    headline={slide.headline}
                    bodyText={slide.body_text}
                    ctaText={slide.cta_text}
                    aspectRatio={config.aspectRatio}
                  />
                ) : null}
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex items-center gap-2">
        <Button onClick={handleCreate} disabled={!canSubmit}>
          <Check className="size-4" />
          إنشاء التصاميم
        </Button>
        <Button type="button" variant="outline" onClick={onBack}>
          رجوع
        </Button>
      </div>
    </div>
  );
}
