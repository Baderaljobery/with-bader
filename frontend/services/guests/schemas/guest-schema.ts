import { z } from "zod";

import type { GuestCreateInput, GuestUpdateInput } from "../types/guest";

/**
 * Mirrors backend/app/schemas/guest.py's GuestCreate: ONLY the name is
 * bilingual (name_ar/name_en, both required). job_title/company/biography
 * stay the plain optional single-value fields they always were - do not
 * reintroduce job_title_ar/en, company_ar/en, industry, country, or
 * biography_ar/en here; that was a past misreading of the requirement.
 */
export const trustedLinkSchema = z.object({
  id: z.string().optional(),
  // Never user-entered - inferred from the URL at submit time (see
  // services/guests/lib/infer-link-label.ts and guest-form-dialog.tsx),
  // so no validation is attached here.
  label: z.string(),
  url: z
    .string()
    .trim()
    .min(1, "الرابط مطلوب")
    .url("أدخل رابطًا صحيحًا (يبدأ بـ https://)"),
});

export const guestFormSchema = z.object({
  name_ar: z.string().trim().min(1, "الاسم بالعربي مطلوب").max(200),
  name_en: z.string().trim().min(1, "الاسم بالإنجليزي مطلوب").max(200),
  job_title: z.string().trim().max(200).optional().or(z.literal("")),
  company: z.string().trim().max(200).optional().or(z.literal("")),
  biography: z.string().trim().max(4000).optional().or(z.literal("")),
  links: z.array(trustedLinkSchema),
});

export type GuestFormValues = z.infer<typeof guestFormSchema>;
export type TrustedLinkFormValue = z.infer<typeof trustedLinkSchema>;

/** The identity fields only - what the backend's GuestCreate/GuestUpdate
 * actually accept (links are created/updated separately, one API call per
 * link, via services/guests/hooks/use-guest-link-mutations.ts). */
export function guestFormValuesToInput(
  values: GuestFormValues
): Omit<GuestCreateInput, "name"> {
  return {
    name_ar: values.name_ar,
    name_en: values.name_en,
    job_title: values.job_title?.trim() || null,
    company: values.company?.trim() || null,
    biography: values.biography?.trim() || null,
  } satisfies GuestUpdateInput;
}
