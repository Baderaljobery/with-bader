import {
  Heading1,
  HelpCircle,
  Lightbulb,
  List,
  ListChecks,
  ListOrdered,
  Megaphone,
  type LucideIcon,
  MessageSquare,
  Minus,
  Quote,
  Sparkles,
  StickyNote,
  Type,
  User,
} from "lucide-react";

import type { BlockType } from "../types/block";

export type BlockTypeMeta = {
  type: BlockType;
  label: string;
  icon: LucideIcon;
  defaultContent: () => Record<string, unknown>;
};

const textContent = () => ({ text: "" });

/** Only backend-supported types with a real editing experience - see
 * types/block.ts for why "image"/"table" are excluded. Order here is the
 * order shown in the block-type insertion menu. */
export const BLOCK_TYPE_REGISTRY: BlockTypeMeta[] = [
  { type: "paragraph", label: "نص", icon: Type, defaultContent: textContent },
  { type: "heading", label: "عنوان", icon: Heading1, defaultContent: textContent },
  { type: "question", label: "سؤال", icon: HelpCircle, defaultContent: textContent },
  { type: "answer", label: "إجابة", icon: MessageSquare, defaultContent: textContent },
  { type: "quote", label: "اقتباس", icon: Quote, defaultContent: textContent },
  { type: "highlight", label: "تمييز", icon: Sparkles, defaultContent: textContent },
  { type: "callout", label: "ملاحظة مهمة", icon: Megaphone, defaultContent: textContent },
  {
    type: "bullet_list",
    label: "قائمة نقطية",
    icon: List,
    defaultContent: () => ({ items: [""] }),
  },
  {
    type: "numbered_list",
    label: "قائمة مرقمة",
    icon: ListOrdered,
    defaultContent: () => ({ items: [""] }),
  },
  {
    type: "checklist",
    label: "قائمة مهام",
    icon: ListChecks,
    defaultContent: () => ({ items: [{ text: "", checked: false }] }),
  },
  { type: "divider", label: "فاصل", icon: Minus, defaultContent: () => ({}) },
  { type: "guest_info", label: "معلومات الضيف", icon: User, defaultContent: textContent },
  { type: "content_idea", label: "فكرة محتوى", icon: Lightbulb, defaultContent: textContent },
  { type: "personal_note", label: "ملاحظة شخصية", icon: StickyNote, defaultContent: textContent },
];

const REGISTRY_BY_TYPE = new Map(BLOCK_TYPE_REGISTRY.map((meta) => [meta.type, meta]));

export function getBlockTypeMeta(type: BlockType): BlockTypeMeta {
  return REGISTRY_BY_TYPE.get(type) ?? BLOCK_TYPE_REGISTRY[0];
}
