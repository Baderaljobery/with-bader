/**
 * Mirrors backend/app/schemas/block.py / app/models/block.py (BLOCK_TYPES)
 * exactly for the type enum and top-level fields.
 *
 * `content` is untyped JSONB on the backend (`dict[str, Any]`) with no
 * server-side shape enforcement per type - there is no existing persisted
 * convention to match, so the shapes below are this frontend's own minimal
 * convention (see services/notebook/lib/block-content.ts for safe readers).
 *
 * "image" and "table" are part of the backend's BLOCK_TYPES enum but are
 * intentionally NOT exposed as creatable types here - there is no upload
 * pipeline or structured table editor backing them yet, and shipping a
 * block type with no reliable way to fill it in would be a fake feature.
 * See the feature's final report for details.
 */
export type BlockType =
  | "heading"
  | "paragraph"
  | "question"
  | "answer"
  | "quote"
  | "highlight"
  | "bullet_list"
  | "numbered_list"
  | "checklist"
  | "divider"
  | "callout"
  | "guest_info"
  | "content_idea"
  | "personal_note";

export type TextBlockContent = { text: string };
export type ListBlockContent = { items: string[] };
export type ChecklistItem = { text: string; checked: boolean };
export type ChecklistBlockContent = { items: ChecklistItem[] };

export type Block = {
  id: string;
  page_id: string;
  type: BlockType;
  content: Record<string, unknown>;
  position: number;
  is_important: boolean;
  is_potential_content: boolean;
  linked_question_id: string | null;
  created_at: string;
  updated_at: string;
};

export type BlockCreateInput = {
  type: BlockType;
  content: Record<string, unknown>;
  position: number;
  is_important?: boolean;
  is_potential_content?: boolean;
  linked_question_id?: string | null;
};

export type BlockUpdateInput = {
  type?: BlockType;
  content?: Record<string, unknown>;
  position?: number;
  is_important?: boolean;
  is_potential_content?: boolean;
  linked_question_id?: string | null;
};
