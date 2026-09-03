"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SLIDE_ROLE_DESCRIPTIONS, SLIDE_ROLE_LABELS, SLIDE_ROLES } from "../lib/labels";
import type { SlideRole, SlideRoleAssignment } from "../types/design";

type SlideRoleSetupProps = {
  slideCount: number;
  roles: SlideRoleAssignment[];
  onChange: (roles: SlideRoleAssignment[]) => void;
  disabled?: boolean;
};

/** Exactly `slideCount` rows, each with an independent role choice - no
 * forced sequence (Part 4/5): any valid role is allowed on any slide,
 * including a single main_content slide with no cover at all. */
export function SlideRoleSetup({ slideCount, roles, onChange, disabled }: SlideRoleSetupProps) {
  function setRole(index: number, role: SlideRole) {
    onChange(roles.map((item) => (item.index === index ? { ...item, role } : item)));
  }

  return (
    <div className="space-y-2">
      {Array.from({ length: slideCount }, (_, i) => i + 1).map((index) => {
        const current = roles.find((item) => item.index === index)?.role ?? "main_content";
        return (
          <div
            key={index}
            className="flex items-center gap-3 rounded-2xl border border-border bg-white px-3 py-2.5"
          >
            <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-secondary text-sm font-semibold text-foreground">
              {index}
            </span>
            <div className="min-w-0 flex-1">
              <Select value={current} onValueChange={(next) => setRole(index, next as SlideRole)} disabled={disabled}>
                <SelectTrigger className="w-full" aria-label={`دور الشريحة ${index}`}>
                  <SelectValue>{(selected: SlideRole) => SLIDE_ROLE_LABELS[selected]}</SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {SLIDE_ROLES.map((role) => (
                    <SelectItem key={role} value={role}>
                      {SLIDE_ROLE_LABELS[role]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <p className="hidden max-w-40 shrink-0 text-xs text-muted-foreground sm:block">
              {SLIDE_ROLE_DESCRIPTIONS[current]}
            </p>
          </div>
        );
      })}
    </div>
  );
}
