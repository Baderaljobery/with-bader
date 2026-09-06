"use client";

import { Palette, RotateCcw, Save, ShieldCheck, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useApproveContent } from "../hooks/use-approve-content";
import { useSaveContent } from "../hooks/use-save-content";
import { useUpdateContent } from "../hooks/use-update-content";
import { LENGTH_LABELS, PLATFORM_LABELS } from "../lib/labels";
import type {
  ContentDraft,
  ContentLength,
  ContentPlatform,
  ContentSourceCategory,
  ContentStatus,
} from "../types/content";
import { SourceTransparency } from "./source-transparency";

export type EditorDraft = {
  id: string | null;
  platform: ContentPlatform;
  length: ContentLength;
  title: string | null;
  content: string;
  sourceContext: ContentSourceCategory[];
  aiProvider: string | null;
  aiModel: string | null;
  status: ContentStatus;
};

type ContentEditorProps = {
  guestId: string;
  draft: EditorDraft;
  onRegenerate: () => void;
  onCancel: () => void;
  onSaved: (draft: ContentDraft) => void;
};

/** Preview-first editor: nothing here is persisted until the user explicitly
 * clicks "حفظ كمسودة" or "إرسال إلى التصميم" (which saves first, then
 * navigates - see handleSendToDesign). Editing never auto-saves. */
export function ContentEditor({ guestId, draft, onRegenerate, onCancel, onSaved }: ContentEditorProps) {
  const router = useRouter();
  const saveContent = useSaveContent(guestId);
  const updateContent = useUpdateContent(guestId);
  const approveContent = useApproveContent(guestId);

  const [title, setTitle] = useState(draft.title ?? "");
  const [content, setContent] = useState(draft.content);
  const [currentId, setCurrentId] = useState(draft.id);
  const [status, setStatus] = useState<ContentStatus>(draft.status);

  const isSaving = saveContent.isPending || updateContent.isPending;

  async function persist(): Promise<ContentDraft> {
    if (currentId) {
      return updateContent.mutateAsync({
        contentId: currentId,
        input: { title: title.trim() || null, content },
      });
    }
    const saved = await saveContent.mutateAsync({
      platform: draft.platform,
      length: draft.length,
      title: title.trim() || null,
      content,
      source_context: draft.sourceContext,
      ai_provider: draft.aiProvider,
      ai_model: draft.aiModel,
    });
    setCurrentId(saved.id);
    return saved;
  }

  async function handleSave() {
    const saved = await persist();
    onSaved(saved);
  }

  async function handleSendToDesign() {
    // "content must be persisted first, then navigate with its ID" - never
    // duplicate the content itself into the query param.
    const saved = await persist();
    router.push(`/guests/${guestId}/design?content=${saved.id}`);
  }

  function handleApprove() {
    if (!currentId) return;
    approveContent.mutate(currentId, {
      onSuccess: (updated) => setStatus(updated.status),
    });
  }

  const canSubmit = content.trim().length > 0 && !isSaving;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-foreground">
            {PLATFORM_LABELS[draft.platform]}
          </span>
          <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-foreground">
            {LENGTH_LABELS[draft.length]}
          </span>
          {status === "approved" ? (
            <Badge className="border-0 bg-emerald-50 font-normal text-emerald-700">معتمد</Badge>
          ) : null}
        </div>
        <Button type="button" variant="ghost" size="icon-sm" aria-label="إلغاء" onClick={onCancel}>
          <X className="size-4" />
        </Button>
      </div>

      <SourceTransparency sources={draft.sourceContext} />

      <div className="space-y-3">
        <Input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="عنوان (اختياري)"
          className="font-heading text-base font-medium"
        />
        <Textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          rows={12}
          className="min-h-64 text-sm leading-7"
          aria-label="نص المحتوى"
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" variant="outline" onClick={onRegenerate} disabled={isSaving}>
          <RotateCcw className="size-4" />
          إعادة التوليد
        </Button>
        <Button type="button" variant="outline" onClick={handleSave} disabled={!canSubmit}>
          <Save className="size-4" />
          حفظ كمسودة
        </Button>
        <Button type="button" onClick={handleSendToDesign} disabled={!canSubmit}>
          <Palette className="size-4" />
          إرسال إلى التصميم
        </Button>
        {currentId && status !== "approved" ? (
          <Button
            type="button"
            variant="outline"
            onClick={handleApprove}
            disabled={approveContent.isPending}
          >
            <ShieldCheck className="size-4" />
            اعتماد المحتوى
          </Button>
        ) : null}
      </div>
    </div>
  );
}
