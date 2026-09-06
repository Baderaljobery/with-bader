"use client";

import { useGuestContent } from "@/services/content/hooks/use-guest-content";
import { LENGTH_LABELS as CONTENT_LENGTH_LABELS, PLATFORM_LABELS as CONTENT_PLATFORM_LABELS } from "@/services/content/lib/labels";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";

const NONE_VALUE = "__none__";

type ContentSourceSelectProps = {
  guestId: string;
  value: string | null;
  onChange: (contentDraftId: string | null) => void;
  disabled?: boolean;
};

/** Lets the user pick an existing saved content draft as the design's
 * primary source - preferred over the supporting Q&A picker below it (see
 * question-picker.tsx), matching the backend's own source priority. */
export function ContentSourceSelect({ guestId, value, onChange, disabled }: ContentSourceSelectProps) {
  const { data: drafts, isPending } = useGuestContent(guestId);

  if (isPending) {
    return <Skeleton className="h-9 w-full" />;
  }

  if (!drafts || drafts.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        لا يوجد محتوى محفوظ لهذا الضيف - يمكنك الاعتماد على إجابات محددة من المقابلة بدلًا من ذلك.
      </p>
    );
  }

  return (
    <Select
      value={value ?? NONE_VALUE}
      onValueChange={(next) => onChange(next === NONE_VALUE ? null : next)}
      disabled={disabled}
    >
      <SelectTrigger className="w-full" aria-label="اختر محتوى محفوظًا">
        <SelectValue placeholder="اختر محتوى محفوظًا">
          {(selected: string | null) => {
            if (!selected || selected === NONE_VALUE) return "بدون محتوى محفوظ (استخدم إجابات محددة)";
            const draft = drafts.find((item) => item.id === selected);
            if (!draft) return "اختر محتوى محفوظًا";
            return `${CONTENT_PLATFORM_LABELS[draft.platform]} · ${CONTENT_LENGTH_LABELS[draft.length]} · ${draft.title || draft.content.slice(0, 40)}`;
          }}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={NONE_VALUE}>بدون محتوى محفوظ (استخدم إجابات محددة)</SelectItem>
        {drafts.map((draft) => (
          <SelectItem key={draft.id} value={draft.id}>
            {CONTENT_PLATFORM_LABELS[draft.platform]} · {CONTENT_LENGTH_LABELS[draft.length]} ·{" "}
            {draft.title || draft.content.slice(0, 40)}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
