"use client";

import { History } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/format-date";
import { useGuestResearchHistory } from "../hooks/use-guest-research-history";

type ResearchVersionHistoryProps = {
  guestId: string;
  latestId: string;
  activeResearchId: string;
  onSelectVersion: (researchId: string | null) => void;
};

export function ResearchVersionHistory({
  guestId,
  latestId,
  activeResearchId,
  onSelectVersion,
}: ResearchVersionHistoryProps) {
  const [open, setOpen] = useState(false);
  const history = useGuestResearchHistory(guestId, { enabled: open });

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger render={<Button variant="outline" size="sm" />}>
        <History className="size-4" />
        الإصدارات السابقة
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="min-w-56">
        {history.isPending ? (
          <div className="px-2 py-1.5 text-xs text-muted-foreground">جارٍ التحميل...</div>
        ) : history.isError ? (
          <div className="px-2 py-1.5 text-xs text-muted-foreground">تعذر تحميل الإصدارات</div>
        ) : (
          [...history.data]
            .sort((a, b) => b.version - a.version)
            .map((item) => (
              <DropdownMenuItem
                key={item.id}
                onClick={() => onSelectVersion(item.id === latestId ? null : item.id)}
                className={cn("justify-between", item.id === activeResearchId && "bg-accent")}
              >
                <span>
                  الإصدار {item.version}
                  {item.id === latestId ? " (الأحدث)" : ""}
                </span>
                <span className="text-xs text-muted-foreground">{formatDate(item.created_at)}</span>
              </DropdownMenuItem>
            ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
