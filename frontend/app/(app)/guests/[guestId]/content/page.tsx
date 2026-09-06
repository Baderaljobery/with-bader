"use client";

import { Plus } from "lucide-react";
import { useParams } from "next/navigation";
import { useState } from "react";

import { SectionHeader } from "@/components/shared/section-header";
import { Button } from "@/components/ui/button";
import { ContentDraftsList } from "@/services/content/components/content-drafts-list";
import { ContentEditor, type EditorDraft } from "@/services/content/components/content-editor";
import { GenerationForm, type GeneratedFrom } from "@/services/content/components/generation-form";
import type { ContentDraft, ContentGenerationResponse } from "@/services/content/types/content";

type Mode =
  | { view: "list" }
  | { view: "create"; initial?: GeneratedFrom }
  | { view: "editor"; draft: EditorDraft };

export default function GuestContentPage() {
  const { guestId } = useParams<{ guestId: string }>();
  const [mode, setMode] = useState<Mode>({ view: "list" });

  function handleGenerated(result: ContentGenerationResponse, request: GeneratedFrom) {
    setMode({
      view: "editor",
      draft: {
        id: null,
        platform: request.platform,
        length: request.length,
        title: result.title,
        content: result.content,
        sourceContext: result.sources_used,
        aiProvider: result.ai_provider,
        aiModel: result.ai_model,
        status: "draft",
      },
    });
  }

  function handleOpenExisting(draft: ContentDraft) {
    setMode({
      view: "editor",
      draft: {
        id: draft.id,
        platform: draft.platform,
        length: draft.length,
        title: draft.title,
        content: draft.content,
        sourceContext: draft.source_context,
        aiProvider: draft.ai_provider,
        aiModel: draft.ai_model,
        status: draft.status,
      },
    });
  }

  function handleRegenerate() {
    if (mode.view !== "editor") return;
    setMode({
      view: "create",
      initial: {
        platform: mode.draft.platform,
        length: mode.draft.length,
        customInstructions: "",
      },
    });
  }

  return (
    <div className="space-y-6">
      <SectionHeader
        title="المحتوى"
        description="حوّل البحث والمقابلة والملاحظات إلى محتوى جاهز للمراجعة."
        action={
          mode.view === "list" ? (
            <Button onClick={() => setMode({ view: "create" })}>
              <Plus className="size-4" />
              إنشاء محتوى
            </Button>
          ) : undefined
        }
      />

      {mode.view === "list" ? (
        <ContentDraftsList
          guestId={guestId}
          onOpen={handleOpenExisting}
          onCreate={() => setMode({ view: "create" })}
        />
      ) : mode.view === "create" ? (
        <div className="mx-auto w-full max-w-2xl rounded-2xl border border-border bg-white p-6 shadow-[var(--shadow-soft)]">
          <GenerationForm
            guestId={guestId}
            initial={mode.initial}
            onGenerated={handleGenerated}
            onCancel={() => setMode({ view: "list" })}
          />
        </div>
      ) : (
        <div className="mx-auto w-full max-w-2xl rounded-2xl border border-border bg-white p-6 shadow-[var(--shadow-soft)]">
          <ContentEditor
            guestId={guestId}
            draft={mode.draft}
            onRegenerate={handleRegenerate}
            onCancel={() => setMode({ view: "list" })}
            onSaved={() => setMode({ view: "list" })}
          />
        </div>
      )}
    </div>
  );
}
