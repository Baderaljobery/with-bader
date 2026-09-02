import { z } from "zod";

export const generationFormSchema = z.object({
  count: z.number().int().min(1, "أقل عدد 1").max(20, "أقصى عدد 20"),
  language: z.enum(["ar", "en"]),
  style: z.string().min(1),
  include_followups: z.boolean(),
});

export type GenerationFormValues = z.infer<typeof generationFormSchema>;
