import { ApiError } from "@/lib/api/client";

/** For POST .../content/generate - the 409 (insufficient context) case is
 * handled separately/inline by the caller (see generation-form.tsx), never
 * as a generic toast, since it needs its own dedicated empty-context UI. */
export function mapContentGenerationError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 504:
        return "استغرق إنشاء المحتوى وقتًا أطول من المتوقع. حاول مرة أخرى.";
      case 502:
        return "تعذر الاتصال بخدمة إنشاء المحتوى. حاول مرة أخرى.";
      case 500:
        return "تعذر إعداد خدمة إنشاء المحتوى.";
      default:
        return "تعذر إنشاء المحتوى، حاول مرة أخرى.";
    }
  }
  return "تعذر إنشاء المحتوى، حاول مرة أخرى.";
}

export function mapContentError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 404:
        return "تعذر العثور على المحتوى. ربما تم حذفه بالفعل.";
      default:
        return "حدث خطأ ما، حاول مرة أخرى.";
    }
  }
  return "حدث خطأ ما، حاول مرة أخرى.";
}
