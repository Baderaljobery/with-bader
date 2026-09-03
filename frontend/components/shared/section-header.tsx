import type { ReactNode } from "react";

type SectionHeaderProps = {
  title: string;
  description?: string;
  action?: ReactNode;
};

/**
 * In-context header for a guest-workspace tab's own content (Research,
 * Questions, Interview, Notebook) - deliberately smaller than PageHeader
 * (text-lg, not text-2xl) since the guest's own name is already the real
 * page title above the tabs. Matches the sizing ResearchHeader already
 * used before this component existed (see features/research/components/
 * research-header.tsx), extracted here so Questions/Interview stop
 * rendering a PageHeader-sized title that outsizes the guest name.
 */
export function SectionHeader({ title, description, action }: SectionHeaderProps) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3 border-b border-border/70 pb-4">
      <div className="space-y-1">
        <h2 className="font-heading text-xl font-semibold tracking-tight text-foreground">
          {title}
        </h2>
        {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
      </div>
      {action}
    </div>
  );
}
