import { Loader2 } from "lucide-react";

/** Single-request operation (upload + transcription happen server-side in
 * one call) - a clean loading state only, never a fake percentage or
 * simulated backend progress. */
export function TranscriptionLoadingState() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-border bg-secondary/40 px-6 py-16 text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white shadow-sm">
        <Loader2 className="size-7 animate-spin" aria-hidden="true" />
      </div>
      <div className="space-y-1">
        <p className="font-heading text-base font-medium text-foreground">جارٍ استخراج النص...</p>
        <p className="text-sm text-muted-foreground">قد تستغرق العملية عدة ثوانٍ حسب حجم الملف.</p>
      </div>
    </div>
  );
}
