"use client";

import { useState } from "react";
import { toast } from "sonner";

import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AudioUploadCard } from "@/features/text-extract/components/audio-upload-card";
import { TranscriptionLoadingState } from "@/features/text-extract/components/transcription-loading-state";
import { TranscriptionResultCard } from "@/features/text-extract/components/transcription-result-card";
import { useAudioTextExtract } from "@/features/text-extract/hooks/use-audio-text-extract";
import { mapTextExtractError } from "@/features/text-extract/lib/error-messages";
import type { TranscriptionResponse } from "@/features/text-extract/types/transcription";

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

      <div className="mx-auto w-full max-w-2xl space-y-6">
        {result ? (
          <TranscriptionResultCard result={result} onUploadAnother={handleUploadAnother} />
        ) : (
          <Card>
            <CardContent className="space-y-4">
              {isPending ? (
                <TranscriptionLoadingState />
              ) : (
                <>
                  <AudioUploadCard
                    file={file}
                    error={fileError}
                    onFileSelect={handleFileSelect}
                    disabled={isPending}
                  />

                  <p className="text-xs text-muted-foreground">
                    يتم استخدام الملف لاستخراج النص فقط، ولا يتم الاحتفاظ بالملف الصوتي بعد
                    المعالجة.
                  </p>

                  <div className="flex items-center gap-2">
                    <Button onClick={handleExtract} disabled={!file || isPending}>
                      استخراج النص
                    </Button>
                    {file || fileError ? (
                      <Button type="button" variant="outline" onClick={handleReset}>
                        مسح
                      </Button>
                    ) : null}
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
