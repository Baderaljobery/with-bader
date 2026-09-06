import { Plus } from "lucide-react";

export function AddGuestCard({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="relative flex min-h-[144px] flex-col items-center justify-center gap-2.5 overflow-hidden rounded-2xl bg-[image:var(--gradient-primary)] text-white shadow-[0_10px_28px_-12px_rgba(27,143,234,0.55)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_18px_36px_-12px_rgba(27,143,234,0.6)] hover:brightness-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
    >
      <span
        aria-hidden="true"
        className="pointer-events-none absolute -top-10 start-1/2 size-40 -translate-x-1/2 rounded-full bg-white/10 blur-2xl"
      />
      <span className="relative flex size-10 items-center justify-center rounded-full bg-white/15 text-white">
        <Plus className="size-5" aria-hidden="true" />
      </span>
      <span className="relative text-sm font-medium">إضافة ضيف</span>
    </button>
  );
}
