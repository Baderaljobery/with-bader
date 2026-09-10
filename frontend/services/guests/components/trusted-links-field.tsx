import { Plus, Trash2 } from "lucide-react";
import { useFieldArray, type Control, type FieldErrors, type UseFormRegister } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { GuestFormValues } from "../schemas/guest-schema";

type TrustedLinksFieldProps = {
  control: Control<GuestFormValues>;
  register: UseFormRegister<GuestFormValues>;
  errors: FieldErrors<GuestFormValues>;
};

/**
 * URL-only - no manual type/label picker. The link's type (LinkedIn,
 * YouTube, X, Instagram, Facebook, Website...) is inferred automatically
 * from the URL at submit time (see infer-link-label.ts in
 * guest-form-dialog.tsx), never chosen by the user.
 */
export function TrustedLinksField({ control, register, errors }: TrustedLinksFieldProps) {
  const { fields, append, remove } = useFieldArray({ control, name: "links" });

  return (
    <div className="space-y-3">
      {fields.length === 0 ? (
        <p className="text-sm text-muted-foreground">لا توجد روابط مضافة بعد.</p>
      ) : (
        <div className="space-y-2.5">
          {fields.map((field, index) => (
            <div key={field.id} className="flex items-start gap-2">
              <div className="flex-1 space-y-1">
                <Input
                  dir="ltr"
                  placeholder="https://"
                  className="bg-white text-start"
                  {...register(`links.${index}.url`)}
                />
                {errors.links?.[index]?.url ? (
                  <p className="text-xs text-destructive">{errors.links[index]?.url?.message}</p>
                ) : null}
              </div>

              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label="حذف الرابط"
                onClick={() => remove(index)}
              >
                <Trash2 className="size-4 text-muted-foreground" />
              </Button>
            </div>
          ))}
        </div>
      )}

      <Button type="button" variant="outline" size="sm" onClick={() => append({ label: "", url: "" })}>
        <Plus className="size-4" />
        إضافة رابط آخر
      </Button>
    </div>
  );
}
