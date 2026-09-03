"use client";

import { FileAudio, Mic, X } from "lucide-react";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// Mirrors backend/app/audio/validation.py defaults (STT_ALLOWED_EXTENSIONS /
// STT_MAX_FILE_SIZE_MB) - not fetched dynamically, since the backend does
// not expose a config endpoint for this. Frontend validation is UX only;
// the backend remains the source of truth.
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

type AudioUploadCardProps = {
  file: File | null;
  error: string | null;
  onFileSelect: (file: File | null, error: string | null) => void;
  disabled?: boolean;
};

export function AudioUploadCard({ file, error, onFileSelect, disabled }: AudioUploadCardProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function validateAndSelect(selected: File | null) {
    if (!selected) {
      onFileSelect(null, null);
      return;
    }
    if (!hasAllowedExtension(selected.name)) {
      onFileSelect(null, `صيغة غير مدعومة. الصيغ المدعومة: ${ALLOWED_EXTENSIONS.join(", ")}`);
      return;
    }
    if (selected.size > MAX_FILE_SIZE_BYTES) {
      onFileSelect(null, `حجم الملف يتجاوز الحد الأقصى (${MAX_FILE_SIZE_MB} ميجابايت).`);
      return;
    }
    onFileSelect(selected, null);
  }

  function handleRemove() {
    onFileSelect(null, null);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div className="flex flex-col items-center gap-6 text-center">
      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_EXTENSIONS.join(",")}
        className="sr-only"
        id="text-extract-audio-input"
        disabled={disabled}
        onChange={(event) => validateAndSelect(event.target.files?.[0] ?? null)}
      />

      {file ? (
        <div className="flex items-center gap-3 rounded-2xl border border-border bg-white px-4 py-3 shadow-[var(--shadow-soft)]">
          <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-secondary text-[#1B8FEA]">
            <FileAudio className="size-4.5" aria-hidden="true" />
          </span>
          <div className="min-w-0 text-start">
            <p className="max-w-56 truncate text-sm font-medium text-foreground">{file.name}</p>
            <p className="text-xs text-muted-foreground">{formatFileSize(file.size)}</p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            aria-label="إزالة الملف"
            onClick={handleRemove}
            disabled={disabled}
          >
            <X className="size-4" />
          </Button>
        </div>
      ) : (
        <label
          htmlFor="text-extract-audio-input"
          onDragOver={(event) => {
            event.preventDefault();
            if (!disabled) setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(event) => {
            event.preventDefault();
            setIsDragging(false);
            if (disabled) return;
            validateAndSelect(event.dataTransfer.files?.[0] ?? null);
          }}
          className={cn(
            "group flex flex-col items-center gap-5",
            disabled ? "pointer-events-none opacity-60" : "cursor-pointer",
          )}
        >
          <div
            className={cn(
              "relative flex size-28 items-center justify-center transition-transform duration-300",
              isDragging ? "scale-105" : "group-hover:-translate-y-1",
            )}
          >
            <div
              className={cn(
                "flex size-24 flex-col items-center justify-center gap-1.5 rounded-2xl border bg-white shadow-[var(--shadow-elevated)] transition-colors",
                isDragging ? "border-[#1B8FEA]" : "border-border",
              )}
            >
              <span className="h-1.5 w-10 rounded-full bg-secondary" />
              <span className="h-1.5 w-12 rounded-full bg-secondary" />
              <span className="h-1.5 w-8 rounded-full bg-secondary" />
            </div>
            <span className="absolute -top-3 -end-3 flex size-10 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white shadow-[0_8px_20px_-6px_rgba(27,143,234,0.55)]">
              <Mic className="size-4.5" aria-hidden="true" />
            </span>
          </div>

          <div className="space-y-1.5">
            <p className="font-heading text-xl font-semibold text-foreground">
              اسحب الملف هنا أو اضغط للاختيار
            </p>
            <p className="text-sm text-muted-foreground">
              الصيغ المدعومة: {ALLOWED_EXTENSIONS.join(", ")} · بحد أقصى {MAX_FILE_SIZE_MB} ميجابايت
            </p>
          </div>
        </label>
      )}

      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
