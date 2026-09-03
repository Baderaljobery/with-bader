"use client";

import { Sparkles } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api/client";
import { AspectRatioSelect } from "./aspect-ratio-select";
import { ContentSourceSelect } from "./content-source-select";
import { GenerationLoadingState } from "./generation-loading-state";
import { NotebookBlockPicker } from "./notebook-block-picker";
import { PlatformSelect } from "./platform-select";
import { QuestionPicker } from "./question-picker";
import { SlideCountSelector } from "./slide-count-selector";
import { SlideRoleSetup } from "./slide-role-setup";
import { TemplatePicker } from "./template-picker";
import { usePlanDesign } from "../hooks/use-plan-design";
import { mapDesignPlanError } from "../lib/error-messages";
import { DESIGN_TEMPLATES, getDesignTemplateById } from "../templates/registry";
import type {
  DesignAspectRatio,
  DesignPlanResponse,
  DesignPlatform,
  SlideRoleAssignment,
} from "../types/design";

export type DesignConfig = {
  contentDraftId: string | null;
  questionIds: string[];
  notebookBlockIds: string[];
  templateId: string;
  slideCount: number;
  slideRoles: SlideRoleAssignment[];
  platform: DesignPlatform;
  aspectRatio: DesignAspectRatio;
  customInstructions: string;
};

type ConfigurationFormProps = {
  guestId: string;
  initialContentDraftId?: string | null;
  onPlanned: (plan: DesignPlanResponse, config: DesignConfig) => void;
  onCancel?: () => void;
};

function resizeRoles(current: SlideRoleAssignment[], count: number): SlideRoleAssignment[] {
  return Array.from({ length: count }, (_, i) => {
    const index = i + 1;
    return current.find((role) => role.index === index) ?? { index, role: "main_content" };
  });
}

const DEFAULT_TEMPLATE_ID = DESIGN_TEMPLATES[0]?.id ?? "";

export function ConfigurationForm({
  guestId,
  initialContentDraftId,
  onPlanned,
  onCancel,
}: ConfigurationFormProps) {
  const planDesign = usePlanDesign(guestId);

  const [contentDraftId, setContentDraftId] = useState<string | null>(initialContentDraftId ?? null);
  const [questionIds, setQuestionIds] = useState<string[]>([]);
  const [notebookBlockIds, setNotebookBlockIds] = useState<string[]>([]);
  const [templateId, setTemplateId] = useState<string>(DEFAULT_TEMPLATE_ID);
  const [slideCount, setSlideCount] = useState(1);
  const [slideRoles, setSlideRoles] = useState<SlideRoleAssignment[]>([{ index: 1, role: "main_content" }]);
  const [platform, setPlatform] = useState<DesignPlatform>("linkedin");
  const [aspectRatio, setAspectRatio] = useState<DesignAspectRatio>("1:1");
  const [customInstructions, setCustomInstructions] = useState("");
  const [insufficientContext, setInsufficientContext] = useState(false);

  const template = getDesignTemplateById(templateId);
  const allowedRatios = template?.supportedAspectRatios ?? ["1:1"];

  function handleSlideCountChange(count: number) {
    setSlideCount(count);
    setSlideRoles((current) => resizeRoles(current, count));
  }

  function handleTemplateChange(nextTemplateId: string) {
    setTemplateId(nextTemplateId);
    // Part 35: never keep a ratio the newly-selected template doesn't
    // actually support - fall back to its first supported ratio instead.
    const next = getDesignTemplateById(nextTemplateId);
    if (next && !next.supportedAspectRatios.includes(aspectRatio)) {
      setAspectRatio(next.supportedAspectRatios[0] ?? "1:1");
    }
  }

  function handleSubmit() {
    if (!templateId) return;
    setInsufficientContext(false);

    const config: DesignConfig = {
      contentDraftId,
      questionIds,
      notebookBlockIds,
      templateId,
      slideCount,
      slideRoles,
      platform,
      aspectRatio,
      customInstructions,
    };

    planDesign.mutate(
      {
        content_draft_id: contentDraftId,
        question_ids: questionIds,
        notebook_block_ids: notebookBlockIds,
        template_id: templateId,
        slide_count: slideCount,
        slide_roles: slideRoles,
        platform,
        custom_instructions: customInstructions.trim() || null,
      },
      {
        onSuccess: (plan) => onPlanned(plan, config),
        onError: (error) => {
          if (error instanceof ApiError && error.status === 409) {
            setInsufficientContext(true);
            return;
          }
          toast.error(mapDesignPlanError(error));
        },
      },
    );
  }

  if (planDesign.isPending) {
    return <GenerationLoadingState message="جارٍ تجهيز محتوى الشرائح..." />;
  }

  if (insufficientContext) {
    return (
      <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border bg-secondary/40 px-6 py-14 text-center">
        <p className="font-heading text-base font-medium text-foreground">
          لا توجد معلومات كافية لإنشاء تصميم لهذا الضيف بعد.
        </p>
        <p className="max-w-sm text-sm text-muted-foreground">
          اختر محتوى محفوظًا أو أجب عن بعض الأسئلة في المقابلة، ثم حاول مرة أخرى.
        </p>
        <Button type="button" variant="outline" onClick={() => setInsufficientContext(false)}>
          رجوع
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-7">
      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">المصدر: محتوى محفوظ</p>
        <ContentSourceSelect guestId={guestId} value={contentDraftId} onChange={setContentDraftId} />
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">أسئلة داعمة (اختياري)</p>
        <QuestionPicker guestId={guestId} value={questionIds} onChange={setQuestionIds} />
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">ملاحظات من الدفتر (اختياري)</p>
        <NotebookBlockPicker guestId={guestId} value={notebookBlockIds} onChange={setNotebookBlockIds} />
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">اختر القالب</p>
        <TemplatePicker value={templateId} onChange={handleTemplateChange} />
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">عدد الشرائح</p>
        <SlideCountSelector value={slideCount} onChange={handleSlideCountChange} />
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">دور كل شريحة</p>
        <SlideRoleSetup slideCount={slideCount} roles={slideRoles} onChange={setSlideRoles} />
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">لأي منصة؟</p>
        <PlatformSelect value={platform} onChange={setPlatform} />
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">أبعاد التصميم</p>
        <AspectRatioSelect value={aspectRatio} onChange={setAspectRatio} allowed={allowedRatios} />
        <p className="text-xs text-muted-foreground">
          الأبعاد المتاحة تعتمد على القالب المختار - كل قالب مصمَّم فعليًا لأبعاد محددة فقط.
        </p>
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">تعليمات إضافية للمحتوى (اختياري)</p>
        <Textarea
          value={customInstructions}
          onChange={(event) => setCustomInstructions(event.target.value)}
          placeholder="مثال: اجعل النص أكثر اختصارًا، ركّز على دروس المسيرة المهنية، أبرز اقتباسًا واحدًا..."
          rows={3}
        />
        <p className="text-xs text-muted-foreground">
          هذه التعليمات تُوجّه المحتوى المكتوب فقط - شكل القالب وألوانه وخطوطه ثابتة ولا تتأثر بها.
        </p>
      </div>

      <div className="flex items-center gap-2">
        <Button onClick={handleSubmit} disabled={!templateId}>
          <Sparkles className="size-4" />
          تجهيز محتوى الشرائح
        </Button>
        {onCancel ? (
          <Button type="button" variant="outline" onClick={onCancel}>
            إلغاء
          </Button>
        ) : null}
      </div>
    </div>
  );
}
