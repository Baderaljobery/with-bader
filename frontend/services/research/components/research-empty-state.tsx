import { Search } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";

type ResearchEmptyStateProps = {
  onStart: () => void;
  isPending: boolean;
};

export function ResearchEmptyState({ onStart, isPending }: ResearchEmptyStateProps) {
  return (
    <EmptyState
      icon={Search}
      title="لم يتم إجراء بحث عن هذا الضيف بعد"
      description="ابدأ البحث لجمع معلومات موثوقة عن المسيرة المهنية والإنجازات والمصادر ذات الصلة."
      action={
        <Button onClick={onStart} disabled={isPending}>
          {isPending ? "جارٍ البحث..." : "بدء البحث"}
        </Button>
      }
    />
  );
}
