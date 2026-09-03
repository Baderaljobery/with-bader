import type { ChecklistItem } from "../types/block";

/**
 * Defensive readers for Block.content - the backend stores arbitrary JSONB
 * with no shape validation, so a value written by a future/older frontend
 * convention (or missing entirely) must never crash the editor.
 */

export function getBlockText(content: Record<string, unknown>): string {
  const text = content.text;
  return typeof text === "string" ? text : "";
}

export function getBlockItems(content: Record<string, unknown>): string[] {
  const items = content.items;
  if (!Array.isArray(items)) return [];
  return items.filter((item): item is string => typeof item === "string");
}

export function getChecklistItems(content: Record<string, unknown>): ChecklistItem[] {
  const items = content.items;
  if (!Array.isArray(items)) return [];
  return items
    .filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null)
    .map((item) => ({
      text: typeof item.text === "string" ? item.text : "",
      checked: Boolean(item.checked),
    }));
}
