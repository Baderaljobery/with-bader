import { Plus } from "lucide-react";

export function AddGuestCard({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex min-h-[132px] flex-col items-center justify-center gap-2 rounded-xl bg-[image:var(--gradient-primary)] text-white shadow-[0_1px_2px_rgba(22,22,22,0.04)] transition-all hover:-translate-y-0.5 hover:shadow-md hover:brightness-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
    >
      <span className="flex size-9 items-center justify-center rounded-full bg-white/15 text-white">
        <Plus className="size-5" aria-hidden="true" />
      </span>
      <span className="text-sm font-medium">إضافة ضيف</span>
    </button>
  );
}
