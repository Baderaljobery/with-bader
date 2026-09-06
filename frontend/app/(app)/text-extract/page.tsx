"use client";

import { Sparkles } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { AudioUploadCard } from "@/services/text-extract/components/audio-upload-card";
import { TranscriptionLoadingState } from "@/services/text-extract/components/transcription-loading-state";
import { TranscriptionResultCard } from "@/services/text-extract/components/transcription-result-card";
import { useAudioTextExtract } from "@/services/text-extract/hooks/use-audio-text-extract";
import { mapTextExtractError } from "@/services/text-extract/lib/error-messages";
import type { TranscriptionResponse } from "@/services/text-extract/types/transcription";

// A faint hairline grid, contained within the hero panel below - the same
// "soft premium background" mood as the reference composition, reinterpreted
// with With Bader's own surface tokens rather than the reference's colors.
const GRID_BACKGROUND = {
  backgroundImage:
    "linear-gradient(to left, rgba(15, 23, 42, 0.05) 1px, transparent 1px), linear-gradient(to top, rgba(15, 23, 42, 0.05) 1px, transparent 1px)",
  backgroundSize: "36px 36px",
};

export default function TextExtractPage() {
  const extractAudio = useAudioTextExtract();
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [result, setResult] = useState<TranscriptionResponse | null>(null);

  function handleFileSelect(selected: File | null, error: string | null) {
    setFile(selected);
    setFileError(error);
  }

  function handleReset() {
    setFile(null);
    setFileError(null);
    extractAudio.reset();
  }

  function handleUploadAnother() {
    setFile(null);
    setFileError(null);
    setResult(null);
    extractAudio.reset();
  }

  function handleExtract() {
    if (!file) return;
    extractAudio.mutate(file, {
      onSuccess: (data) => {
        setResult(data);
        // Nothing about the audio itself is retained client-side once the
        // request completes.
        setFile(null);
      },
      onError: (error) => {
        toast.error(mapTextExtractError(error));
      },
    });
  }

  const isPending = extractAudio.isPending;

  return (
    <div className="space-y-6">
      <PageHeader
        title="استخراج النصوص"
        description="ارفع ملفًا صوتيًا لتحويله إلى نص عربي بسرعة."
      />

      <div className="relative mx-auto w-full max-w-3xl overflow-hidden rounded-[2rem] border border-border bg-white shadow-[var(--shadow-elevated)]">
        <div aria-hidden="true" className="absolute inset-0" style={GRID_BACKGROUND} />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-24 start-1/2 size-96 -translate-x-1/2 rounded-full opacity-60 blur-3xl"
          style={{ backgroundImage: "var(--glow-teal)" }}
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute bottom-[-6rem] end-[-4rem] size-72 rounded-full opacity-50 blur-3xl"
          style={{ backgroundImage: "var(--glow-blue)" }}
        />

        <div className="relative">
          {result ? (
            <div className="p-6 sm:p-10">
              <TranscriptionResultCard result={result} onUploadAnother={handleUploadAnother} />
            </div>
          ) : isPending ? (
            <div className="flex flex-col items-center justify-center px-6 py-20 sm:py-24">
              <TranscriptionLoadingState />
            </div>
          ) : (
            <div className="flex flex-col items-center gap-8 px-6 py-16 sm:py-20">
              <AudioUploadCard
                file={file}
                error={fileError}
                onFileSelect={handleFileSelect}
                disabled={isPending}
              />

              <div className="flex flex-col items-center gap-3">
                <p className="max-w-xs text-center text-xs text-muted-foreground">
                  يتم استخدام الملف لاستخراج النص فقط، ولا يتم الاحتفاظ بالملف الصوتي بعد المعالجة.
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    size="lg"
                    className="rounded-full px-8"
                    onClick={handleExtract}
                    disabled={!file || isPending}
                  >
                    <Sparkles className="size-4" />
                    استخراج النص
                  </Button>
                  {file || fileError ? (
                    <Button type="button" variant="outline" className="rounded-full" onClick={handleReset}>
                      مسح
                    </Button>
                  ) : null}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
