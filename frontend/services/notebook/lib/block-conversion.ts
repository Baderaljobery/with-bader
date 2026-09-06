import { getBlockText } from "./block-content";
import { getBlockTypeMeta } from "./block-types";
import type { Block, BlockType } from "../types/block";

/** All types whose content is the same `{ text }` shape - switching among
 * these preserves the written text ("change type if safe", per spec).
 * Anything outside this set (list/checklist/divider) has a different
 * content shape, so switching to/from it resets content to that type's
 * default rather than guessing a lossy conversion. */
const TEXT_LIKE_TYPES: readonly BlockType[] = [
  "heading",
  "paragraph",
  "question",
  "answer",
  "quote",
  "highlight",
  "callout",
  "guest_info",
  "content_idea",
  "personal_note",
];

export function contentForTypeChange(block: Block, newType: BlockType): Record<string, unknown> {
  if (TEXT_LIKE_TYPES.includes(block.type) && TEXT_LIKE_TYPES.includes(newType)) {
    return { text: getBlockText(block.content) };
  }
  return getBlockTypeMeta(newType).defaultContent();
}
