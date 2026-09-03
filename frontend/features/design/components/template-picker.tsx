"use client";

import { Check } from "lucide-react";

import { cn } from "@/lib/utils";
import { DESIGN_TEMPLATES } from "../templates/registry";

type TemplatePickerProps = {
  value: string | null;
  onChange: (templateId: string) => void;
  disabled?: boolean;
};

/** Real visual preview cards, never a plain <select> - the user must see
 * and manually choose a template (Part 2/31): no AI ranking, no
 * auto-select, no hidden default beyond the first render's empty state. */
export function TemplatePicker({ value, onChange, disabled }: TemplatePickerProps) {
  return (
    <div
      role="radiogroup"
      aria-label="اختر قالب التصميم"
      className="grid grid-cols-2 gap-3 sm:grid-cols-4"
    >
      {DESIGN_TEMPLATES.map((template) => {
        const active = value === template.id;
        return (
          <button
            key={template.id}
            type="button"
            role="radio"
            aria-checked={active}
            disabled={disabled}
            onClick={() => onChange(template.id)}
            className={cn(
              "group relative flex flex-col overflow-hidden rounded-2xl border text-start transition-all disabled:pointer-events-none disabled:opacity-50",
              active
                ? "border-transparent shadow-[0_10px_24px_-10px_rgba(27,143,234,0.55)] ring-2 ring-[#1B8FEA]"
                : "border-border hover:border-[#1B8FEA]/40",
            )}
          >
            <div className="relative aspect-square w-full overflow-hidden bg-secondary">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={template.preview}
                alt={template.name}
                className="h-full w-full object-cover transition-transform group-hover:scale-105"
              />
              {active ? (
                <span
                  className="absolute end-2 top-2 flex size-6 items-center justify-center rounded-full text-white shadow-sm"
                  style={{ backgroundImage: "var(--gradient-primary)" }}
                >
                  <Check className="size-3.5" aria-hidden="true" />
                </span>
              ) : null}
            </div>
            <div className="space-y-0.5 bg-white p-2.5">
              <p className="text-sm font-medium text-foreground">{template.name}</p>
              <p className="line-clamp-2 text-xs text-muted-foreground">{template.description}</p>
            </div>
          </button>
        );
      })}
    </div>
  );
}
