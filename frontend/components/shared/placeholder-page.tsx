import type { LucideIcon } from "lucide-react";

type PlaceholderPageProps = {
  icon: LucideIcon;
  title: string;
  description: string;
};

export function PlaceholderPage({ icon: Icon, title, description }: PlaceholderPageProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-border bg-secondary/40 px-6 py-24 text-center">
      <div className="flex size-14 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white shadow-sm">
        <Icon className="size-7" aria-hidden="true" />
      </div>
      <div className="space-y-1">
        <p className="font-heading text-base font-medium text-foreground">{title}</p>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}
