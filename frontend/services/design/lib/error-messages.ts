import { ApiError } from "@/lib/api/client";

/** For POST .../designs/plan - the 409 (insufficient context) case is
 * handled separately/inline by the caller (see configuration-form.tsx),
 * never as a generic toast. */
export function mapDesignPlanError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 504:
        return "استغرق تجهيز محتوى الشرائح وقتًا أطول من المتوقع. حاول مرة أخرى.";
      case 502:
        return "تعذر الاتصال بخدمة تجهيز المحتوى. حاول مرة أخرى.";
      case 500:
        return "تعذر إعداد خدمة تجهيز المحتوى.";
      default:
        return "تعذر تجهيز محتوى الشرائح، حاول مرة أخرى.";
    }
  }
  return "تعذر تجهيز محتوى الشرائح، حاول مرة أخرى.";
}

export function mapDesignError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 404:
        return "تعذر العثور على التصميم. ربما تم حذفه بالفعل.";
      default:
        return "حدث خطأ ما، حاول مرة أخرى.";
    }
  }
  return "حدث خطأ ما، حاول مرة أخرى.";
}
