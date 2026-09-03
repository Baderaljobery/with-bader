"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
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
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api/client";
import { useCreateGuest, useUpdateGuest } from "../hooks/use-guest-mutations";
import { guestFormSchema, guestFormValuesToInput, type GuestFormValues } from "../schemas/guest-schema";
import type { Guest } from "../types/guest";

type GuestFormDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  guest?: Guest;
};

function defaultValuesFor(guest?: Guest): GuestFormValues {
  return {
    name: guest?.name ?? "",
    job_title: guest?.job_title ?? "",
    company: guest?.company ?? "",
    biography: guest?.biography ?? "",
  };
}

export function GuestFormDialog({ open, onOpenChange, guest }: GuestFormDialogProps) {
  const isEdit = Boolean(guest);
  const createGuest = useCreateGuest();
  const updateGuest = useUpdateGuest(guest?.id ?? "");
  const mutation = isEdit ? updateGuest : createGuest;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<GuestFormValues>({
    resolver: zodResolver(guestFormSchema),
    defaultValues: defaultValuesFor(guest),
  });

  useEffect(() => {
    if (open) {
      reset(defaultValuesFor(guest));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, guest]);

  const onSubmit = handleSubmit(async (values) => {
    try {
      await mutation.mutateAsync(guestFormValuesToInput(values));
      toast.success(isEdit ? "تم تحديث بيانات الضيف" : "تمت إضافة الضيف");
      onOpenChange(false);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "حدث خطأ ما.";
      toast.error(message);
    }
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={onSubmit} className="space-y-4">
          <DialogHeader>
            <DialogTitle>{isEdit ? "تعديل بيانات الضيف" : "إضافة ضيف"}</DialogTitle>
            <DialogDescription>
              {isEdit
                ? "قم بتحديث المعلومات الأساسية لهذا الضيف."
                : "أضف ضيفًا جديدًا لتبدأ تحضير مقابلته."}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-1.5">
            <Label htmlFor="guest-name">الاسم</Label>
            <Input id="guest-name" autoFocus {...register("name")} />
            {errors.name ? (
              <p className="text-xs text-destructive">{errors.name.message}</p>
            ) : null}
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="guest-job-title">المسمى الوظيفي</Label>
              <Input id="guest-job-title" {...register("job_title")} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="guest-company">الشركة</Label>
              <Input id="guest-company" {...register("company")} />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="guest-biography">نبذة تعريفية</Label>
            <Textarea id="guest-biography" rows={4} {...register("biography")} />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              إلغاء
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "جارٍ الحفظ..." : isEdit ? "حفظ التغييرات" : "إضافة ضيف"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
