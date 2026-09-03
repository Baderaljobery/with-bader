"use client";

import { Copy, RotateCcw } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TranscriptionResponse } from "../types/transcription";

type TranscriptionResultCardProps = {
  result: TranscriptionResponse;
  onUploadAnother: () => void;
};

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
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3">
        <CardTitle>النص المستخرج</CardTitle>
        <div className="flex items-center gap-2">
          <Button type="button" variant="outline" size="sm" onClick={handleCopy}>
            <Copy className="size-3.5" aria-hidden="true" />
            نسخ النص
          </Button>
          <Button type="button" variant="outline" size="sm" onClick={onUploadAnother}>
            <RotateCcw className="size-3.5" aria-hidden="true" />
            رفع ملف آخر
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="max-h-[28rem] overflow-y-auto rounded-lg border border-border bg-secondary/30 p-4">
          <p className="text-sm leading-7 whitespace-pre-wrap text-foreground select-text">
            {result.text}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
          {result.language ? <span>اللغة: {result.language}</span> : null}
          {result.duration_seconds != null ? (
            <span>مدة الملف: {result.duration_seconds.toFixed(1)} ثانية</span>
          ) : null}
          <span>المزوّد: {result.provider}</span>
          <span>النموذج: {result.model}</span>
        </div>
      </CardContent>
    </Card>
  );
}
