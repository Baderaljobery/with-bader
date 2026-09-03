import type { ForwardRefExoticComponent, RefAttributes } from "react";

import type { DesignAspectRatio, SlideRole } from "../types/design";

export type DesignTemplateFontFamily = "sans" | "serif-display" | "serif-text";

/** Approximate content budget for one role within one template - fed to the
 * planner's prompt as brevity guidance (see
 * backend/app/design_planning/prompts.py) and used client-side to size the
 * live overflow warning check (Part 11/13). Not a hard character limit the
 * UI enforces by truncating - a genuinely-too-long slide should surface a
 * warning, never silently render unreadable text. */
export type ContentLimits = {
  headlineMaxChars: number;
  bodyMaxChars?: number;
  maxPoints?: number;
};

export type SlideRenderProps = {
  role: SlideRole;
  headline: string;
  bodyText: string;
  ctaText?: string | null;
  aspectRatio: DesignAspectRatio;
  className?: string;
};

export type TemplateDefinition = {
  id: string;
  name: string;
  description: string;
  /** Original reference image this template's visual design is based on -
   * shown in the template picker and never used as runtime AI input
   * anymore (Part 5/18). */
  preview: string;
  fontFamily: DesignTemplateFontFamily;
  supportedAspectRatios: DesignAspectRatio[];
  contentLimits: Record<SlideRole, ContentLimits>;
  /** The actual deterministic renderer - real frontend code, not an AI
   * call. Same template + same content always produces the same visual
   * output (Part 6). Forwards a ref to its root DOM node so the editor can
   * export it to a real PNG (Part 32/33). */
  Renderer: ForwardRefExoticComponent<SlideRenderProps & RefAttributes<HTMLDivElement>>;
};
