"use client";

import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

const UPLOAD_STAGES = ["جارٍ رفع الملف...", "جارٍ استخراج النص...", "جارٍ مطابقة الإجابات بالأسئلة..."];
const STAGE_INTERVAL_MS = 2500;

type InterviewLoadingStateProps = {
  mode: "transcribing" | "matching";
};

/** Purely visual stage cycling for the single transcribe-interview request
 * (which does upload+STT+matching server-side in one call) - never a real
 * progress signal, never a percentage. */
export function InterviewLoadingState({ mode }: InterviewLoadingStateProps) {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    if (mode !== "transcribing") return;
    const interval = setInterval(() => {
      setStageIndex((index) => (index + 1) % UPLOAD_STAGES.length);
    }, STAGE_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [mode]);

  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-border bg-secondary/40 px-6 py-20 text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white shadow-sm">
        <Loader2 className="size-7 animate-spin" aria-hidden="true" />
      </div>
      <div className="space-y-1">
        <p className="font-heading text-base font-medium text-foreground">
          {mode === "transcribing" ? "جارٍ معالجة المقابلة..." : "جارٍ إعادة مطابقة الإجابات..."}
        </p>
      </div>
      <p className="text-xs font-medium text-[#1B8FEA]" role="status" aria-live="polite">
        {mode === "transcribing" ? UPLOAD_STAGES[stageIndex] : "جارٍ مطابقة الإجابات بالأسئلة..."}
      </p>
    </div>
  );
}
