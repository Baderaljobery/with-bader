import { ApiError } from "@/lib/api/client";

/**
 * Maps known backend status codes (see backend/app/api/guest_interview.py)
 * to friendly Arabic copy. Never surfaces the raw upstream provider/backend
 * message for unmapped cases - a generic fallback is used instead.
 */
export function mapInterviewUploadError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 413:
        return "حجم الملف كبير جدًا. الحد الأقصى المسموح به 25 ميجابايت.";
      case 415:
        return "صيغة الملف غير مدعومة. الصيغ المدعومة: MP3, WAV, FLAC, OGG, M4A.";
      case 422:
        return "تعذرت معالجة الملف الصوتي. تحقق من الملف وحاول مرة أخرى.";
      case 502:
        return "تعذر الاتصال بخدمة تحويل الصوت إلى نص. حاول مرة أخرى.";
      case 504:
        return "استغرقت معالجة الملف وقتًا طويلاً. حاول مرة أخرى.";
      default:
        return "تعذر رفع المقابلة، حاول مرة أخرى";
    }
  }
  return "تعذر رفع المقابلة، حاول مرة أخرى";
}

export function mapMatchingError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 422:
        return "نص المقابلة طويل جدًا على محرك المطابقة. جرّب اختصار النص.";
      case 502:
        return "تعذر الاتصال بخدمة مطابقة الإجابات. حاول مرة أخرى.";
      case 504:
        return "استغرقت مطابقة الإجابات وقتًا طويلاً. حاول مرة أخرى.";
      default:
        return "تعذرت إعادة مطابقة الإجابات، حاول مرة أخرى";
    }
  }
  return "تعذرت إعادة مطابقة الإجابات، حاول مرة أخرى";
}
