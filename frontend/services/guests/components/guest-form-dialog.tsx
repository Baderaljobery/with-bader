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
import { guestLinksApi } from "../api/guest-links-api";
import { useCreateGuestLink, useDeleteGuestLink, useUpdateGuestLink } from "../hooks/use-guest-link-mutations";
import { useCreateGuest, useUpdateGuest } from "../hooks/use-guest-mutations";
import { useGuestLinks } from "../hooks/use-guest-links";
import { inferLinkLabel } from "../lib/infer-link-label";
import {
  guestFormSchema,
  guestFormValuesToInput,
  type GuestFormValues,
  type TrustedLinkFormValue,
} from "../schemas/guest-schema";
import type { Guest } from "../types/guest";
import { TrustedLinksField } from "./trusted-links-field";

type GuestFormDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  guest?: Guest;
};

function defaultValuesFor(guest: Guest | undefined, links: TrustedLinkFormValue[]): GuestFormValues {
  return {
    name_ar: guest?.name_ar ?? "",
    name_en: guest?.name_en ?? "",
    job_title: guest?.job_title ?? "",
    company: guest?.company ?? "",
    biography: guest?.biography ?? "",
    links,
  };
}

export function GuestFormDialog({ open, onOpenChange, guest }: GuestFormDialogProps) {
  const isEdit = Boolean(guest);
  const createGuest = useCreateGuest();
  const updateGuest = useUpdateGuest(guest?.id ?? "");
  const createLink = useCreateGuestLink(guest?.id ?? "");
  const updateLink = useUpdateGuestLink(guest?.id ?? "");
  const deleteLink = useDeleteGuestLink(guest?.id ?? "");
  const { data: existingLinks } = useGuestLinks(guest?.id ?? "");

  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<GuestFormValues>({
    resolver: zodResolver(guestFormSchema),
    defaultValues: defaultValuesFor(guest, []),
  });

  useEffect(() => {
    if (!open) return;
    const links: TrustedLinkFormValue[] =
      existingLinks?.map((link) => ({ id: link.id, label: link.label, url: link.url })) ?? [];
    reset(defaultValuesFor(guest, links));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, guest, existingLinks]);

  async function reconcileLinks(guestId: string, submittedLinks: TrustedLinkFormValue[]) {
    const originalById = new Map((existingLinks ?? []).map((link) => [link.id, link]));
    const submittedIds = new Set(submittedLinks.filter((l) => l.id).map((l) => l.id));

    const results = await Promise.allSettled([
      // New links (no id yet): always infer the type fresh from the URL.
      ...submittedLinks
        .filter((link) => !link.id)
        .map((link) =>
          createLink.mutateAsync({ label: inferLinkLabel(link.url), url: link.url })
        ),
      // Existing links: only touched (and re-inferred) if the URL itself was
      // actually edited - an untouched link keeps its previously-saved
      // label as-is, so a guest already using the old type picker never
      // has its classification silently rewritten by re-saving the form.
      ...submittedLinks
        .filter((link) => {
          if (!link.id) return false;
          const original = originalById.get(link.id);
          return Boolean(original && original.url !== link.url);
        })
        .map((link) =>
          updateLink.mutateAsync({
            linkId: link.id as string,
            input: { label: inferLinkLabel(link.url), url: link.url },
          })
        ),
      ...(existingLinks ?? [])
        .filter((link) => !submittedIds.has(link.id))
        .map((link) => deleteLink.mutateAsync(link.id)),
    ]);

    if (results.some((r) => r.status === "rejected")) {
      toast.error("تم حفظ بيانات الضيف، لكن تعذر حفظ بعض الروابط.");
    }
  }

  const onSubmit = handleSubmit(async (values) => {
    try {
      const input = guestFormValuesToInput(values);
      if (isEdit && guest) {
        await updateGuest.mutateAsync(input);
        await reconcileLinks(guest.id, values.links);
        toast.success("تم تحديث بيانات الضيف");
      } else {
        const newGuest = await createGuest.mutateAsync(input);
        if (values.links.length > 0) {
          // Not routed through useCreateGuestLink here: that hook is bound
          // to `guest?.id` at render time, which is still empty in create
          // mode (the guest didn't exist yet) - call the API directly with
          // the just-created guest's real id instead.
          const linkResults = await Promise.allSettled(
            values.links.map((link) =>
              guestLinksApi.create(newGuest.id, { label: inferLinkLabel(link.url), url: link.url })
            )
          );
          if (linkResults.some((r) => r.status === "rejected")) {
            toast.error("تمت إضافة الضيف، لكن تعذر حفظ بعض الروابط.");
          }
        }
        toast.success("تمت إضافة الضيف");
      }
      onOpenChange(false);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "حدث خطأ ما.";
      toast.error(message);
    }
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[85vh] flex-col sm:max-w-md">
        <form onSubmit={onSubmit} className="flex min-h-0 flex-1 flex-col">
          <DialogHeader>
            <DialogTitle>{isEdit ? "تعديل بيانات الضيف" : "إضافة ضيف"}</DialogTitle>
            <DialogDescription>
              {isEdit
                ? "قم بتحديث المعلومات الأساسية لهذا الضيف."
                : "أضف ضيفًا جديدًا لتبدأ تحضير مقابلته. الاسم بالعربي والإنجليزي يساعد على بحث أدق."}
            </DialogDescription>
          </DialogHeader>

          <div className="-mx-6 flex-1 space-y-4 overflow-y-auto px-6 py-4">
            <div className="space-y-1.5">
              <Label htmlFor="guest-name-ar">الاسم بالعربي *</Label>
              <Input id="guest-name-ar" dir="rtl" autoFocus {...register("name_ar")} />
              {errors.name_ar ? (
                <p className="text-xs text-destructive">{errors.name_ar.message}</p>
              ) : null}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="guest-name-en">الاسم بالإنجليزي *</Label>
              <Input id="guest-name-en" dir="ltr" {...register("name_en")} />
              {errors.name_en ? (
                <p className="text-xs text-destructive">{errors.name_en.message}</p>
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

            <div className="space-y-2 border-t border-[#E6EAF0] pt-4">
              <div className="space-y-1">
                <h3 className="font-heading text-sm font-semibold text-[#161616]">روابط موثوقة</h3>
                <p className="text-xs text-[#5F6368]">اختياري - لينكدإن، الموقع الرسمي، أو أي رابط عام موثوق.</p>
              </div>
              <TrustedLinksField control={control} register={register} errors={errors} />
            </div>
          </div>

          <DialogFooter className="border-t border-[#E6EAF0] pt-4">
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
