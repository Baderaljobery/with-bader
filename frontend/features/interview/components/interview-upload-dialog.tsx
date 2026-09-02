"use client";

import { FileAudio, Upload, X } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ApiError } from "@/lib/api/client";
import { useTranscribeGuestInterview } from "../hooks/use-transcribe-interview";
import { mapInterviewUploadError } from "../lib/error-messages";
import type { GuestInterviewMatchResponse } from "../types/interview";
import { InterviewLoadingState } from "./interview-loading-state";

// Mirrors backend/app/audio/validation.py defaults (STT_ALLOWED_EXTENSIONS /
// STT_MAX_FILE_SIZE_MB) - not fetched dynamically, since the backend does
// not expose a config endpoint for this.
const ALLOWED_EXTENSIONS = [".mp3", ".wav", ".flac", ".ogg", ".m4a"];
const MAX_FILE_SIZE_MB = 25;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

function formatFileSize(bytes: number) {
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(mb < 1 ? 2 : 1)} ميجابايت`;
}

function hasAllowedExtension(filename: string) {
  const lower = filename.toLowerCase();
  return ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

type InterviewUploadDialogProps = {
  guestId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  hasExistingTranscript: boolean;
  onTranscribed: (result: GuestInterviewMatchResponse) => void;
};

export function InterviewUploadDialog({
  guestId,
  open,
  onOpenChange,
  hasExistingTranscript,
  onTranscribed,
}: InterviewUploadDialogProps) {
  const transcribeInterview = useTranscribeGuestInterview(guestId);
  const [file, setFile] = useState<File | null>(null);
  const [confirmingReplace, setConfirmingReplace] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function resetLocalState() {
    setFile(null);
    setConfirmingReplace(false);
    setFileError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  function handleOpenChange(nextOpen: boolean) {
    if (!nextOpen) {
      resetLocalState();
      transcribeInterview.reset();
    }
    onOpenChange(nextOpen);
  }

  function handleFileSelect(selected: File | null) {
    setFileError(null);
    if (!selected) {
      setFile(null);
      return;
    }
    if (!hasAllowedExtension(selected.name)) {
      setFileError(`صيغة غير مدعومة. الصيغ المدعومة: ${ALLOWED_EXTENSIONS.join(", ")}`);
      setFile(null);
      return;
    }
    if (selected.size > MAX_FILE_SIZE_BYTES) {
      setFileError(`حجم الملف يتجاوز الحد الأقصى (${MAX_FILE_SIZE_MB} ميجابايت).`);
      setFile(null);
      return;
    }
    setFile(selected);
  }

  function runTranscribe(replaceExisting: boolean) {
    if (!file) return;
    transcribeInterview.mutate(
      { file, replaceExisting },
      {
        onSuccess: (data) => {
          // Clears the selected File from state immediately - nothing about
          // the audio itself is ever retained client-side.
          resetLocalState();
          onOpenChange(false);
          onTranscribed(data);
          toast.success("تم رفع المقابلة ومطابقة الإجابات بنجاح");
        },
        onError: (error) => {
          if (error instanceof ApiError && error.status === 409) {
            setConfirmingReplace(true);
            return;
          }
          toast.error(mapInterviewUploadError(error));
        },
      },
    );
  }

  function handleSubmit() {
    if (!file) return;
    if (hasExistingTranscript) {
      setConfirmingReplace(true);
      return;
    }
    runTranscribe(false);
  }

  const isPending = transcribeInterview.isPending;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        {isPending ? (
          <InterviewLoadingState mode="transcribing" />
        ) : confirmingReplace ? (
          <div className="space-y-4">
            <DialogHeader>
              <DialogTitle>يوجد نص مقابلة محفوظ بالفعل</DialogTitle>
              <DialogDescription>يوجد نص مقابلة محفوظ لهذا الضيف بالفعل.</DialogDescription>
            </DialogHeader>
            <p className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
              سيتم استبدال نص المقابلة الحالي وإعادة مطابقة الإجابات المستخرجة آليًا. لن يتم
              استبدال الإجابات اليدوية.
            </p>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setConfirmingReplace(false)}>
                إلغاء
              </Button>
              <Button variant="destructive" onClick={() => runTranscribe(true)}>
                استبدال المقابلة الحالية
              </Button>
            </DialogFooter>
          </div>
        ) : (
          <div className="space-y-4">
            <DialogHeader>
              <DialogTitle>رفع ملف المقابلة</DialogTitle>
              <DialogDescription>
                سيتم استخراج نص المقابلة تلقائيًا وربط الإجابات بالأسئلة المحفوظة.
              </DialogDescription>
            </DialogHeader>

            <div>
              <input
                ref={inputRef}
                type="file"
                accept={ALLOWED_EXTENSIONS.join(",")}
                className="sr-only"
                id="interview-audio-input"
                onChange={(event) => handleFileSelect(event.target.files?.[0] ?? null)}
              />

              {file ? (
                <div className="flex items-center gap-3 rounded-lg border border-[#E6EAF0] p-3">
                  <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-[#F7F8FA] text-[#1B8FEA]">
                    <FileAudio className="size-4" aria-hidden="true" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-[#161616]">{file.name}</p>
                    <p className="text-xs text-[#5F6368]">{formatFileSize(file.size)}</p>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-sm"
                    aria-label="إزالة الملف"
                    onClick={() => handleFileSelect(null)}
                  >
                    <X className="size-4" />
                  </Button>
                </div>
              ) : (
                <label
                  htmlFor="interview-audio-input"
                  className="flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed border-[#E6EAF0] px-4 py-8 text-center transition-colors hover:border-[#1B8FEA]/40 hover:bg-[#F7F8FA]"
                >
                  <Upload className="size-6 text-[#5F6368]" aria-hidden="true" />
                  <span className="text-sm font-medium text-[#161616]">
                    اختر ملف الصوت أو اسحبه هنا
                  </span>
                  <span className="text-xs text-[#5F6368]">
                    الصيغ المدعومة: {ALLOWED_EXTENSIONS.join(", ")} · بحد أقصى {MAX_FILE_SIZE_MB}{" "}
                    ميجابايت
                  </span>
                </label>
              )}

              {fileError ? <p className="mt-2 text-xs text-destructive">{fileError}</p> : null}
            </div>

            <p className="text-xs text-muted-foreground">
              يتم استخدام الملف لاستخراج النص فقط، ولا يتم الاحتفاظ بالملف الصوتي بعد المعالجة.
            </p>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => handleOpenChange(false)}>
                إلغاء
              </Button>
              <Button onClick={handleSubmit} disabled={!file}>
                رفع ومعالجة
              </Button>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
