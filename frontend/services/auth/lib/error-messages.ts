import { ApiError } from "@/lib/api/client";

export function mapLoginError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        // Deliberately the same message whether the email doesn't exist
        // or the password is wrong - the backend never reveals which.
        return "البريد الإلكتروني أو كلمة المرور غير صحيحة.";
      case 422:
        return "يرجى إدخال بريد إلكتروني وكلمة مرور صحيحين.";
      default:
        return "تعذر تسجيل الدخول، حاول مرة أخرى.";
    }
  }
  return "تعذر تسجيل الدخول، حاول مرة أخرى.";
}

export function mapRegisterError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 409:
        return "هذا البريد الإلكتروني مسجّل بالفعل.";
      case 422:
        return "يرجى مراجعة البيانات المدخلة.";
      default:
        return "تعذر إنشاء الحساب، حاول مرة أخرى.";
    }
  }
  return "تعذر إنشاء الحساب، حاول مرة أخرى.";
}
