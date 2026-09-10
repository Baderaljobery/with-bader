import { Search } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import type { Guest } from "@/services/guests/types/guest";
import { isGuestResearchReady, ResearchReadiness } from "./research-readiness";

type ResearchEmptyStateProps = {
  guest: Guest;
  onStart: () => void;
  isPending: boolean;
};

export function ResearchEmptyState({ guest, onStart, isPending }: ResearchEmptyStateProps) {
  const ready = isGuestResearchReady(guest);

  return (
    <div className="space-y-4">
      <ResearchReadiness guest={guest} />
      {ready ? (
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
      ) : null}
    </div>
  );
}
