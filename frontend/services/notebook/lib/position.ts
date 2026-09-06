/**
 * Position helpers. Block.position is a float (fractional positioning
 * supported natively by the backend - see app/models/block.py), so
 * inserting between two blocks never requires renumbering the rest of the
 * page. NotebookPage.position is a plain non-negative integer with no
 * fractional support, so pages only ever get appended (no page reordering
 * in this phase) using a simple +1 increment.
 */

const BLOCK_POSITION_GAP = 1000;

export function nextBlockPosition(blocks: { position: number }[]): number {
  if (blocks.length === 0) return BLOCK_POSITION_GAP;
  return Math.max(...blocks.map((block) => block.position)) + BLOCK_POSITION_GAP;
}

/** Position for a block inserted at `index` within `orderedBlocks` (already
 * sorted by position, ascending). Used both for "+" insertion between two
 * existing blocks and for computing a moved block's new position after a
 * drag-and-drop reorder. */
export function positionForIndex(orderedBlocks: { position: number }[], index: number): number {
  const before = orderedBlocks[index - 1]?.position;
  const after = orderedBlocks[index]?.position;

  if (before === undefined && after === undefined) return BLOCK_POSITION_GAP;
  if (before === undefined) return after! - BLOCK_POSITION_GAP;
  if (after === undefined) return before + BLOCK_POSITION_GAP;

  const midpoint = (before + after) / 2;
  // Guard against float precision collapsing the gap after many inserts in
  // the same spot - still land strictly between the two neighbors.
  if (midpoint <= before || midpoint >= after) return before + (after - before) / 1000;
  return midpoint;
}

export function nextPagePosition(pages: { position: number }[]): number {
  if (pages.length === 0) return 0;
  return Math.max(...pages.map((page) => page.position)) + 1;
}
