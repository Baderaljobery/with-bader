"use client";

import { Plus } from "lucide-react";
import { useParams, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { SectionHeader } from "@/components/shared/section-header";
import { Button } from "@/components/ui/button";
import { ConfigurationForm, type DesignConfig } from "@/features/design/components/configuration-form";
import { DesignDraftsList } from "@/features/design/components/design-drafts-list";
import { MultiSlideEditor } from "@/features/design/components/multi-slide-editor";
import { StructurePreview } from "@/features/design/components/structure-preview";
import type { DesignDraft, DesignPlanResponse } from "@/features/design/types/design";

type Mode =
  | { view: "list" }
  | { view: "configure" }
  | { view: "preview"; plan: DesignPlanResponse; config: DesignConfig }
  | { view: "editor"; design: DesignDraft };

function GuestDesignPageContent() {
  const { guestId } = useParams<{ guestId: string }>();
  const searchParams = useSearchParams();
  const initialContentDraftId = searchParams.get("content");

  const [mode, setMode] = useState<Mode>(initialContentDraftId ? { view: "configure" } : { view: "list" });

  return (
    <div className="space-y-6">
      <SectionHeader
        title="التصميم"
        description="حوّل المحتوى المحفوظ وإجابات المقابلة إلى تصميم بصري متعدد الشرائح جاهز للمشاركة."
        action={
          mode.view === "list" ? (
            <Button onClick={() => setMode({ view: "configure" })}>
              <Plus className="size-4" />
              إنشاء تصميم
            </Button>
          ) : undefined
        }
      />

      {mode.view === "list" ? (
        <DesignDraftsList
          guestId={guestId}
          onOpen={(design) => setMode({ view: "editor", design })}
          onCreate={() => setMode({ view: "configure" })}
        />
      ) : mode.view === "configure" ? (
        <div className="mx-auto w-full max-w-2xl rounded-2xl border border-border bg-white p-6 shadow-[var(--shadow-soft)]">
          <ConfigurationForm
            guestId={guestId}
            initialContentDraftId={initialContentDraftId}
            onPlanned={(plan, config) => setMode({ view: "preview", plan, config })}
            onCancel={() => setMode({ view: "list" })}
          />
        </div>
      ) : mode.view === "preview" ? (
        <div className="mx-auto w-full max-w-2xl rounded-2xl border border-border bg-white p-6 shadow-[var(--shadow-soft)]">
          <StructurePreview
            guestId={guestId}
            plan={mode.plan}
            config={mode.config}
            onBack={() => setMode({ view: "configure" })}
            onGenerated={(design) => setMode({ view: "editor", design })}
          />
        </div>
      ) : (
        <div className="mx-auto w-full max-w-2xl rounded-2xl border border-border bg-white p-6 shadow-[var(--shadow-soft)]">
          <MultiSlideEditor
            guestId={guestId}
            design={mode.design}
            onBack={() => setMode({ view: "list" })}
            onDeleted={() => setMode({ view: "list" })}
          />
        </div>
      )}
    </div>
  );
}

export default function GuestDesignPage() {
  return (
    <Suspense fallback={null}>
      <GuestDesignPageContent />
    </Suspense>
  );
}
