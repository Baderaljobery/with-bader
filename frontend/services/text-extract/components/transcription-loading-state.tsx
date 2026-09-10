import { AnimatedLogo } from "@/components/brand/animated-logo";

/** Single-request operation (upload + transcription happen server-side in
 * one call) - a clean loading state only, never a fake percentage or
 * simulated backend progress. Frameless - the page's own hero panel
 * provides the surrounding surface. */
export function TranscriptionLoadingState() {
  return (
    <div className="flex flex-col items-center gap-6 text-center">
      <div className="flex size-24 items-center justify-center rounded-2xl border border-border bg-white p-3.5 shadow-[var(--shadow-elevated)]">
        <AnimatedLogo markOnly className="h-full w-full" />
      </div>
      <div className="space-y-1.5">
        <p className="font-heading text-xl font-semibold text-foreground">جارٍ استخراج النص...</p>
        <p className="text-sm text-muted-foreground">قد تستغرق العملية عدة ثوانٍ حسب حجم الملف.</p>
      </div>
    </div>
  );
}
