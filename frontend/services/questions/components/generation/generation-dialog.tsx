"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Sparkles } from "lucide-react";
import Link from "next/link";
import { useForm, useWatch } from "react-hook-form";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useGenerateQuestions } from "../../hooks/use-generate-questions";
import {
  generationFormSchema,
  type GenerationFormValues,
} from "../../schemas/generation-schema";
import type { QuestionGenerationResponse } from "../../types/question";
import { ApiError } from "@/lib/api/client";

const STYLE_OPTIONS = [
  { value: "conversational", label: "أسلوب حواري" },
  { value: "professional", label: "أسلوب احترافي" },
  { value: "deep", label: "أسئلة معمقة" },
];

type GenerationDialogProps = {
  guestId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onGenerated: (response: QuestionGenerationResponse) => void;
};

export function GenerationDialog({ guestId, open, onOpenChange, onGenerated }: GenerationDialogProps) {
  const generateQuestions = useGenerateQuestions(guestId);

  const { register, handleSubmit, control, setValue } = useForm<GenerationFormValues>({
    resolver: zodResolver(generationFormSchema),
    defaultValues: {
      count: 12,
      language: "ar",
      style: "conversational",
      include_followups: true,
    },
  });

  const language = useWatch({ control, name: "language" });
  const style = useWatch({ control, name: "style" });
  const includeFollowups = useWatch({ control, name: "include_followups" });

  const isNoResearch =
    generateQuestions.isError &&
    generateQuestions.error instanceof ApiError &&
    generateQuestions.error.status === 409;

  const onSubmit = handleSubmit((values) => {
    generateQuestions.mutate(values, {
      onSuccess: (data) => {
        onOpenChange(false);
        generateQuestions.reset();
        onGenerated(data);
      },
      onError: (error) => {
        if (!(error instanceof ApiError && error.status === 409)) {
          toast.error("تعذر إنشاء الأسئلة، حاول مرة أخرى");
        }
      },
    });
  });

  function handleOpenChange(nextOpen: boolean) {
    if (!nextOpen) generateQuestions.reset();
    onOpenChange(nextOpen);
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        {generateQuestions.isPending ? (
          <div className="flex flex-col items-center gap-4 py-6 text-center">
            <div className="flex size-14 items-center justify-center rounded-full bg-[image:var(--gradient-primary)] text-white shadow-sm">
              <Loader2 className="size-7 animate-spin" aria-hidden="true" />
            </div>
            <div className="space-y-1">
              <p className="font-heading text-base font-medium text-foreground">
                جارٍ إنشاء أسئلة مخصصة للضيف...
              </p>
              <p className="text-sm text-muted-foreground">
                يتم الاعتماد على ملف البحث الحالي لإعداد الأسئلة
              </p>
            </div>
          </div>
        ) : isNoResearch ? (
          <div className="space-y-4">
            <DialogHeader>
              <DialogTitle>يلزم إجراء بحث أولًا</DialogTitle>
            </DialogHeader>
            <p className="text-sm text-muted-foreground">
              يجب إكمال بحث الضيف أولًا قبل إنشاء أسئلة بالذكاء الاصطناعي.
            </p>
            <DialogFooter>
              <Button variant="outline" onClick={() => handleOpenChange(false)}>
                إلغاء
              </Button>
              <Button nativeButton={false} render={<Link href={`/guests/${guestId}/research`} />}>
                الانتقال إلى البحث
              </Button>
            </DialogFooter>
          </div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-4">
            <DialogHeader>
              <DialogTitle>إنشاء أسئلة بالذكاء الاصطناعي</DialogTitle>
              <DialogDescription>
                سيتم إنشاء أسئلة مقترحة بناءً على ملف بحث الضيف، ولن يتم حفظها إلا بعد اختيارك.
              </DialogDescription>
            </DialogHeader>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="generation-count">عدد الأسئلة</Label>
                <Input
                  id="generation-count"
                  type="number"
                  min={1}
                  max={20}
                  {...register("count", { valueAsNumber: true })}
                />
              </div>
              <div className="space-y-1.5">
                <Label>اللغة</Label>
                <Select
                  value={language}
                  onValueChange={(value) => value && setValue("language", value as "ar" | "en")}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ar">العربية</SelectItem>
                    <SelectItem value="en">الإنجليزية</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-1.5">
              <Label>أسلوب الأسئلة</Label>
              <Select value={style} onValueChange={(value) => value && setValue("style", value)}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {STYLE_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <label className="flex items-center gap-2 text-sm text-[#5F6368]">
              <Checkbox
                checked={includeFollowups}
                onCheckedChange={(checked) => setValue("include_followups", checked === true)}
              />
              اقترح أسئلة متابعة لكل سؤال
            </label>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => handleOpenChange(false)}>
                إلغاء
              </Button>
              <Button type="submit">
                <Sparkles className="size-4" />
                إنشاء الأسئلة
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
