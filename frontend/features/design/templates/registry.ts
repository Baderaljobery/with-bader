/**
 * Design Engine template registry - THE single authoritative source for
 * every template (Part 25). Combines what used to be split across a
 * picker-only registry (name/description/preview) and a separate
 * generation-time definition: each entry here carries the picker metadata
 * AND the real deterministic Renderer component, the template's fixed
 * font, its supported aspect ratios, and its per-role content limits.
 *
 * The user always picks a template id manually from this list - nothing
 * here is ever chosen automatically (see template-picker.tsx).
 */

import { Template01Renderer } from "./template-01/Renderer";
import { TEMPLATE_01_CONTENT_LIMITS, TEMPLATE_01_DESCRIPTION, TEMPLATE_01_ID, TEMPLATE_01_NAME } from "./template-01/config";
import { Template02Renderer } from "./template-02/Renderer";
import { TEMPLATE_02_CONTENT_LIMITS, TEMPLATE_02_DESCRIPTION, TEMPLATE_02_ID, TEMPLATE_02_NAME } from "./template-02/config";
import { Template03Renderer } from "./template-03/Renderer";
import { TEMPLATE_03_CONTENT_LIMITS, TEMPLATE_03_DESCRIPTION, TEMPLATE_03_ID, TEMPLATE_03_NAME } from "./template-03/config";
import { Template04Renderer } from "./template-04/Renderer";
import { TEMPLATE_04_CONTENT_LIMITS, TEMPLATE_04_DESCRIPTION, TEMPLATE_04_ID, TEMPLATE_04_NAME } from "./template-04/config";
import type { TemplateDefinition } from "./types";

export type { DesignTemplateFontFamily, TemplateDefinition, SlideRenderProps, ContentLimits } from "./types";

export const DESIGN_TEMPLATES: TemplateDefinition[] = [
  {
    id: TEMPLATE_01_ID,
    name: TEMPLATE_01_NAME,
    description: TEMPLATE_01_DESCRIPTION,
    preview: "/design-references/template-01/reference-01.png",
    fontFamily: "serif-display",
    supportedAspectRatios: ["1:1", "4:5", "9:16"],
    contentLimits: TEMPLATE_01_CONTENT_LIMITS,
    Renderer: Template01Renderer,
  },
  {
    id: TEMPLATE_02_ID,
    name: TEMPLATE_02_NAME,
    description: TEMPLATE_02_DESCRIPTION,
    preview: "/design-references/template-02/reference-01.jpg",
    fontFamily: "serif-display",
    supportedAspectRatios: ["1:1", "4:5", "9:16"],
    contentLimits: TEMPLATE_02_CONTENT_LIMITS,
    Renderer: Template02Renderer,
  },
  {
    id: TEMPLATE_03_ID,
    name: TEMPLATE_03_NAME,
    description: TEMPLATE_03_DESCRIPTION,
    preview: "/design-references/template-03/reference-01.png",
    fontFamily: "serif-display",
    supportedAspectRatios: ["1:1", "4:5", "9:16", "16:9"],
    contentLimits: TEMPLATE_03_CONTENT_LIMITS,
    Renderer: Template03Renderer,
  },
  {
    id: TEMPLATE_04_ID,
    name: TEMPLATE_04_NAME,
    description: TEMPLATE_04_DESCRIPTION,
    preview: "/design-references/template-04/reference-01.jpg",
    fontFamily: "sans",
    supportedAspectRatios: ["1:1", "4:5", "16:9"],
    contentLimits: TEMPLATE_04_CONTENT_LIMITS,
    Renderer: Template04Renderer,
  },
];

export function getDesignTemplateById(id: string): TemplateDefinition | undefined {
  return DESIGN_TEMPLATES.find((template) => template.id === id);
}
