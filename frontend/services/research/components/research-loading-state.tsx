"use client";

import { useEffect, useState } from "react";

import { AnimatedLogo } from "@/components/brand/animated-logo";

const STAGES = ["البحث عن المصادر", "تحليل المعلومات", "إعداد الملف البحثي"];
const STAGE_INTERVAL_MS = 2500;

/**
 * Purely visual stage cycling - not tied to any real backend progress
 * signal (the run endpoint is a single request/response, it doesn't report
 * progress). Never presented as a percentage.
 */
export function ResearchLoadingState() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStageIndex((index) => (index + 1) % STAGES.length);
    }, STAGE_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-border bg-secondary/40 px-6 py-20 text-center">
      <div className="flex size-14 items-center justify-center">
        <AnimatedLogo markOnly className="size-14" />
      </div>
      <div className="space-y-1">
        <p className="font-heading text-base font-medium text-foreground">
          جارٍ البحث عن معلومات الضيف...
        </p>
        <p className="text-sm text-muted-foreground">يتم الآن جمع المصادر وتحليلها</p>
      </div>
      <p className="text-xs font-medium text-[#1B8FEA]" role="status" aria-live="polite">
        {STAGES[stageIndex]}
      </p>
    </div>
  );
}
