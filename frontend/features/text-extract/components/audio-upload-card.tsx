"use client";

import { FileAudio, Upload, X } from "lucide-react";
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
    <div>
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
        <div className="flex items-center gap-3 rounded-lg border border-border p-3">
          <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-secondary text-[#1B8FEA]">
            <FileAudio className="size-5" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-foreground">{file.name}</p>
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
            "flex flex-col items-center gap-3 rounded-xl border-2 border-dashed px-4 py-12 text-center transition-colors",
            disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer",
            isDragging
              ? "border-[#1B8FEA] bg-[#F7F8FA]"
              : "border-border hover:border-[#1B8FEA]/40 hover:bg-[#F7F8FA]",
          )}
        >
          <span className="flex size-12 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white">
            <Upload className="size-5" aria-hidden="true" />
          </span>
          <span className="text-sm font-medium text-foreground">اسحب الملف هنا أو اختر ملفًا</span>
          <span className="text-xs text-muted-foreground">
            الصيغ المدعومة: {ALLOWED_EXTENSIONS.join(", ")} · بحد أقصى {MAX_FILE_SIZE_MB} ميجابايت
          </span>
        </label>
      )}

      {error ? <p className="mt-2 text-xs text-destructive">{error}</p> : null}
    </div>
  );
}
