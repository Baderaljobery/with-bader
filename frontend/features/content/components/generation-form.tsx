"use client";

import { Sparkles } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api/client";
import { useGenerateContent } from "../hooks/use-generate-content";
import { mapContentGenerationError } from "../lib/error-messages";
import type { ContentGenerationResponse, ContentLength, ContentPlatform } from "../types/content";
import { GenerationLoadingState } from "./generation-loading-state";
import { LengthSelect } from "./length-select";
import { PlatformSelect } from "./platform-select";

export type GeneratedFrom = {
  platform: ContentPlatform;
  length: ContentLength;
  customInstructions: string;
};

type GenerationFormProps = {
  guestId: string;
  initial?: GeneratedFrom;
  onGenerated: (result: ContentGenerationResponse, request: GeneratedFrom) => void;
  onCancel?: () => void;
};

export function GenerationForm({ guestId, initial, onGenerated, onCancel }: GenerationFormProps) {
  const generateContent = useGenerateContent(guestId);
  const [platform, setPlatform] = useState<ContentPlatform>(initial?.platform ?? "linkedin");
  const [length, setLength] = useState<ContentLength>(initial?.length ?? "medium");
  const [customInstructions, setCustomInstructions] = useState(initial?.customInstructions ?? "");
  const [insufficientContext, setInsufficientContext] = useState(false);

  function handleSubmit() {
    setInsufficientContext(false);
    generateContent.mutate(
      { platform, length, custom_instructions: customInstructions.trim() || null },
      {
        onSuccess: (result) => {
          onGenerated(result, { platform, length, customInstructions: customInstructions.trim() });
        },
        onError: (error) => {
          if (error instanceof ApiError && error.status === 409) {
            setInsufficientContext(true);
            return;
          }
          toast.error(mapContentGenerationError(error));
        },
      },
    );
  }

  if (generateContent.isPending) {
    return <GenerationLoadingState />;
  }

  if (insufficientContext) {
    return (
      <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border bg-secondary/40 px-6 py-14 text-center">
        <p className="font-heading text-base font-medium text-foreground">
          لا توجد معلومات كافية لإنشاء محتوى لهذا الضيف بعد.
        </p>
        <p className="max-w-sm text-sm text-muted-foreground">
          أضف إجابات من المقابلة، ملاحظات في الدفتر، أو أكمل البحث أولًا، ثم حاول مرة أخرى.
        </p>
        <Button type="button" variant="outline" onClick={() => setInsufficientContext(false)}>
          رجوع
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">أين تريد نشر المحتوى؟</p>
        <PlatformSelect value={platform} onChange={setPlatform} />
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">اختر طول المحتوى</p>
        <LengthSelect value={length} onChange={setLength} />
      </div>

      <div className="space-y-2.5">
        <p className="text-sm font-medium text-foreground">تعليمات إضافية (اختياري)</p>
        <Textarea
          value={customInstructions}
          onChange={(event) => setCustomInstructions(event.target.value)}
          placeholder="مثال: ركّز على قصة العودة إلى الشركة..."
          rows={3}
        />
      </div>

      <div className="flex items-center gap-2">
        <Button onClick={handleSubmit}>
          <Sparkles className="size-4" />
          إنشاء المحتوى
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
