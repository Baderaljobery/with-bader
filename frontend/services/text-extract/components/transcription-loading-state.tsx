import { Loader2 } from "lucide-react";

/** Single-request operation (upload + transcription happen server-side in
 * one call) - a clean loading state only, never a fake percentage or
 * simulated backend progress. Frameless - the page's own hero panel
 * provides the surrounding surface. */
export function TranscriptionLoadingState() {
  return (
    <div className="flex flex-col items-center gap-6 text-center">
      <div className="flex size-28 items-center justify-center">
        <div className="relative flex size-24 items-center justify-center rounded-2xl border border-border bg-white shadow-[var(--shadow-elevated)]">
          <span className="absolute -top-3 -end-3 flex size-10 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white shadow-[0_8px_20px_-6px_rgba(27,143,234,0.55)]">
            <Loader2 className="size-4.5 animate-spin" aria-hidden="true" />
          </span>
          <div className="flex flex-col items-center gap-1.5">
            <span className="h-1.5 w-10 rounded-full bg-secondary" />
            <span className="h-1.5 w-12 animate-pulse rounded-full bg-[#1FCFC3]/40" />
            <span className="h-1.5 w-8 rounded-full bg-secondary" />
          </div>
        </div>
      </div>
      <div className="space-y-1.5">
        <p className="font-heading text-xl font-semibold text-foreground">جارٍ استخراج النص...</p>
        <p className="text-sm text-muted-foreground">قد تستغرق العملية عدة ثوانٍ حسب حجم الملف.</p>
      </div>
    </div>
  );
}
