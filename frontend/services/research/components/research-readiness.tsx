"use client";

import { Check, Pencil, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { GuestFormDialog } from "@/services/guests/components/guest-form-dialog";
import { useGuestLinks } from "@/services/guests/hooks/use-guest-links";
import type { Guest } from "@/services/guests/types/guest";

type ReadinessCheck = { label: string; complete: boolean; optional?: boolean };

/**
 * The only REQUIRED research identity information is the bilingual name -
 * mirrors backend's has_complete_bilingual_identity
 * (app/services/guest_service.py). company/job_title/biography/trusted
 * links may improve research quality but never block it - they're shown
 * as optional, informational checks only.
 */
function getIdentityChecks(guest: Guest, trustedLinkCount: number): ReadinessCheck[] {
  return [
    { label: "الاسم بالعربية", complete: Boolean(guest.name_ar?.trim()) },
    { label: "الاسم بالإنجليزية", complete: Boolean(guest.name_en?.trim()) },
    { label: "المسمى الوظيفي", complete: Boolean(guest.job_title?.trim()), optional: true },
    { label: "الشركة", complete: Boolean(guest.company?.trim()), optional: true },
    { label: "نبذة تعريفية", complete: Boolean(guest.biography?.trim()), optional: true },
    { label: "روابط موثوقة", complete: trustedLinkCount > 0, optional: true },
  ];
}

export function isGuestResearchReady(guest: Guest): boolean {
  return getIdentityChecks(guest, 1)
    .filter((check) => !check.optional)
    .every((check) => check.complete);
}

function ChecklistRow({ check }: { check: ReadinessCheck }) {
  return (
    <li className="flex items-center gap-2 text-sm">
      <span
        className={cn(
          "flex size-4.5 shrink-0 items-center justify-center rounded-full",
          check.complete ? "bg-emerald-100 text-emerald-700" : "bg-secondary text-muted-foreground"
        )}
      >
        {check.complete ? (
          <Check className="size-3" aria-hidden="true" />
        ) : (
          <X className="size-3" aria-hidden="true" />
        )}
      </span>
      <span className={check.complete ? "text-[#161616]" : "text-[#5F6368]"}>
        {check.label}
        {check.optional ? <span className="text-xs text-muted-foreground"> (اختياري)</span> : null}
      </span>
    </li>
  );
}

/**
 * Shown before the first research run (Phase 21 - "Research Readiness
 * summary"). For a legacy guest missing the bilingual name, this replaces
 * the ability to start research entirely - research never runs silently
 * against a guest with no usable Arabic/English name.
 */
export function ResearchReadiness({ guest }: { guest: Guest }) {
  const [editOpen, setEditOpen] = useState(false);
  const { data: links } = useGuestLinks(guest.id);
  const checks = getIdentityChecks(guest, links?.length ?? 0);
  const ready = checks.filter((c) => !c.optional).every((c) => c.complete);

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>جاهزية البحث</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <ul className="grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
            {checks.map((check) => (
              <ChecklistRow key={check.label} check={check} />
            ))}
          </ul>
          {!ready ? (
            <div className="space-y-2 rounded-lg border border-dashed border-[#E6EAF0] bg-[#F7F8FA] p-3">
              <p className="text-sm font-medium text-[#161616]">أكمل بيانات الضيف قبل البحث</p>
              <p className="text-xs text-[#5F6368]">
                البحث يحتاج الاسم بالعربية والإنجليزية على الأقل ليعطي نتائج دقيقة عن الشخص الصحيح.
              </p>
              <Button size="sm" variant="outline" onClick={() => setEditOpen(true)}>
                <Pencil className="size-4" />
                تعديل بيانات الضيف
              </Button>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <GuestFormDialog open={editOpen} onOpenChange={setEditOpen} guest={guest} />
    </>
  );
}
