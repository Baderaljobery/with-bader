import { Loader2 } from "lucide-react";

/** No fake progress percentage - a single request/response call. */
export function GenerationLoadingState({ message = "جارٍ إنشاء التصميم..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-dashed border-border bg-secondary/40 px-6 py-16 text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white shadow-sm">
        <Loader2 className="size-7 animate-spin" aria-hidden="true" />
      </div>
      <p className="font-heading text-base font-medium text-foreground">{message}</p>
    </div>
  );
}
