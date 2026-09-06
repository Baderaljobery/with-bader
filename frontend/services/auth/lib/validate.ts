const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const MIN_PASSWORD_LENGTH = 8;

export function validateEmail(email: string): string | null {
  if (!email.trim()) return "البريد الإلكتروني مطلوب.";
  if (!EMAIL_PATTERN.test(email.trim())) return "صيغة البريد الإلكتروني غير صحيحة.";
  return null;
}

export function validatePassword(password: string): string | null {
  if (!password) return "كلمة المرور مطلوبة.";
  if (password.length < MIN_PASSWORD_LENGTH) {
    return `يجب ألا تقل كلمة المرور عن ${MIN_PASSWORD_LENGTH} أحرف.`;
  }
  return null;
}

export function validateName(name: string): string | null {
  if (!name.trim()) return "الاسم مطلوب.";
  return null;
}

export function validateConfirmPassword(password: string, confirmPassword: string): string | null {
  if (!confirmPassword) return "تأكيد كلمة المرور مطلوب.";
  if (password !== confirmPassword) return "كلمتا المرور غير متطابقتين.";
  return null;
}
