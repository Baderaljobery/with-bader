import { z } from "zod";

export const questionFormSchema = z.object({
  text: z.string().trim().min(1, "نص السؤال مطلوب").max(1000),
  topic: z.string().trim().max(200).optional().or(z.literal("")),
});

export type QuestionFormValues = z.infer<typeof questionFormSchema>;

export function questionFormValuesToInput(values: QuestionFormValues) {
  return {
    text: values.text,
    topic: values.topic?.trim() || null,
  };
}
