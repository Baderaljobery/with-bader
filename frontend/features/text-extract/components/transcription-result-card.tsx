"use client";

import { Copy, RotateCcw } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import type { TranscriptionResponse } from "../types/transcription";

type TranscriptionResultCardProps = {
  result: TranscriptionResponse;
  onUploadAnother: () => void;
};

/** Frameless - the page's own hero panel provides the surrounding surface,
 * so this only ever renders the header row + transcript + metadata. */
export function TranscriptionResultCard({ result, onUploadAnother }: TranscriptionResultCardProps) {
  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(result.text);
      toast.success("تم نسخ النص");
    } catch {
      toast.error("تعذر نسخ النص. حدد النص وانسخه يدويًا.");
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/70 pb-4">
        <div className="flex items-center gap-2.5">
          <span className="flex size-9 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white">
            <Copy className="size-4" aria-hidden="true" />
          </span>
          <h2 className="font-heading text-lg font-semibold text-foreground">النص المستخرج</h2>
        </div>
        <div className="flex items-center gap-2">
          <Button type="button" variant="outline" size="sm" className="rounded-full" onClick={handleCopy}>
            <Copy className="size-3.5" aria-hidden="true" />
            نسخ النص
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="rounded-full"
            onClick={onUploadAnother}
          >
            <RotateCcw className="size-3.5" aria-hidden="true" />
            رفع ملف آخر
          </Button>
        </div>
      </div>

      <div className="max-h-[26rem] overflow-y-auto rounded-2xl border border-border/70 bg-secondary/40 p-5">
        <p className="text-sm leading-7 whitespace-pre-wrap text-foreground select-text">{result.text}</p>
      </div>

      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
        {result.language ? <span>اللغة: {result.language}</span> : null}
        {result.duration_seconds != null ? (
          <span>مدة الملف: {result.duration_seconds.toFixed(1)} ثانية</span>
        ) : null}
        <span>المزوّد: {result.provider}</span>
        <span>النموذج: {result.model}</span>
      </div>
    </div>
  );
}
