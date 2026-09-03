import { z } from "zod";

/**
 * Fields intentionally exposed in the Add/Edit Guest form. The backend
 * schema (GuestCreate/GuestUpdate) also supports slug, personal_notes,
 * research_summary, preparation_status, and content_status - those are
 * workspace-managed fields, not part of this quick-create/edit flow.
 */
export const guestFormSchema = z.object({
  name: z.string().trim().min(1, "الاسم مطلوب").max(200),
  job_title: z.string().trim().max(200).optional().or(z.literal("")),
  company: z.string().trim().max(200).optional().or(z.literal("")),
  biography: z.string().trim().max(4000).optional().or(z.literal("")),
});

export type GuestFormValues = z.infer<typeof guestFormSchema>;

export function guestFormValuesToInput(values: GuestFormValues) {
  return {
    name: values.name,
    job_title: values.job_title?.trim() || null,
    company: values.company?.trim() || null,
    biography: values.biography?.trim() || null,
  };
}
