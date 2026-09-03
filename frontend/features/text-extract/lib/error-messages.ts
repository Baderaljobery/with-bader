import { ApiError } from "@/lib/api/client";

/**
 * Maps known backend status codes (see backend/app/api/text_extract.py) to
 * friendly Arabic copy. Never surfaces the raw upstream provider/backend
 * message - a generic fallback is used instead for anything unmapped.
 */
export function mapTextExtractError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 413:
        return "حجم الملف أكبر من الحد المسموح.";
      case 415:
        return "صيغة الملف غير مدعومة.";
      case 422:
        return "تعذر قراءة الملف. تأكد من أن الملف الصوتي صالح.";
      case 500:
        return "تعذر إعداد خدمة استخراج النص.";
      case 502:
        return "حدث خطأ أثناء معالجة الملف.";
      case 504:
        return "استغرقت عملية استخراج النص وقتًا أطول من المتوقع.";
      default:
        return "تعذر استخراج النص، حاول مرة أخرى.";
    }
  }
  return "تعذر استخراج النص، حاول مرة أخرى.";
}
