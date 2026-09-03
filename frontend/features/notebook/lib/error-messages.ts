import { ApiError } from "@/lib/api/client";

/** Never surfaces the raw backend/database error - a generic Arabic
 * fallback is used for anything unmapped. */
export function mapNotebookError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 404:
        return "تعذر العثور على العنصر المطلوب. ربما تم حذفه بالفعل.";
      case 422:
        return "البيانات المُدخلة غير صالحة.";
      default:
        return "حدث خطأ ما، حاول مرة أخرى.";
    }
  }
  return "حدث خطأ ما، حاول مرة أخرى.";
}
