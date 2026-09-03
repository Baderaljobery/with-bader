import { toPng } from "html-to-image";

import { ASPECT_RATIO_PX } from "./shared";
import type { DesignAspectRatio } from "../types/design";

/** Renders one slide's live DOM node to a full-resolution PNG (Part 32/33).
 * The visible editor preview can be any on-screen size (container-query
 * type scale keeps it proportional) - export always requests the template's
 * real social-ready pixel size regardless of how large the node currently
 * renders on screen, via html-to-image's pixelRatio option. */
export async function exportSlideToPng(node: HTMLElement, aspectRatio: DesignAspectRatio): Promise<Blob> {
  // Part 34: never export before the Thmanyah webfonts have actually
  // finished loading, or the PNG can bake in a fallback system font.
  if (typeof document !== "undefined" && "fonts" in document) {
    await document.fonts.ready;
  }

  const target = ASPECT_RATIO_PX[aspectRatio];
  const rect = node.getBoundingClientRect();
  const pixelRatio = rect.width > 0 ? target.width / rect.width : 1;

  const dataUrl = await toPng(node, {
    pixelRatio,
    cacheBust: true,
    backgroundColor: undefined,
  });

  const response = await fetch(dataUrl);
  return response.blob();
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
