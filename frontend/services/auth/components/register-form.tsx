"use client";

import { Eye, EyeOff, Lock, Mail, User } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRegister } from "../hooks/use-register";
import { mapRegisterError } from "../lib/error-messages";
import {
  validateConfirmPassword,
  validateEmail,
  validateName,
  validatePassword,
} from "../lib/validate";

type FieldErrors = {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
};

export function RegisterForm() {
  const router = useRouter();
  const register = useRegister();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // A fast double-click/double-Enter can fire two submit events before
    // React re-renders the button as disabled - this guard closes that
    // window so one submit can never produce two register requests.
    if (register.isPending) return;
    setFormError(null);

    const errors: FieldErrors = {
      name: validateName(name) ?? undefined,
      email: validateEmail(email) ?? undefined,
      password: validatePassword(password) ?? undefined,
      confirmPassword: validateConfirmPassword(password, confirmPassword) ?? undefined,
    };
    setFieldErrors(errors);
    if (Object.values(errors).some(Boolean)) return;

    register.mutate(
      { name: name.trim(), email: email.trim(), password },
      {
        onSuccess: () => {
          toast.success("تم إنشاء الحساب بنجاح");
          // Registration already establishes a real session (the backend
          // auto-authenticates on 201) - replace + refresh straight into
          // the app, never a second manual login step.
          router.replace("/");
          router.refresh();
        },
        onError: (err) => setFormError(mapRegisterError(err)),
      },
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1 text-center">
        <h1 className="font-heading text-lg font-semibold text-[#161616]">إنشاء حساب</h1>
        <p className="text-sm text-[#5F6368]">أنشئ حسابك الخاص لبدء إدارة ضيوفك ومحتواك.</p>
      </div>

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="register-name" className="sr-only">
            الاسم
          </Label>
          <div className="relative">
            <User
              className="pointer-events-none absolute end-3 top-1/2 size-4 -translate-y-1/2 text-[#5F6368]"
              aria-hidden="true"
            />
            <Input
              id="register-name"
              autoComplete="name"
              placeholder="الاسم"
              className="h-10 pe-9"
              aria-invalid={Boolean(fieldErrors.name)}
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
          </div>
          {fieldErrors.name ? <p className="text-xs text-destructive">{fieldErrors.name}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="register-email" className="sr-only">
            البريد الإلكتروني
          </Label>
          <div className="relative">
            <Mail
              className="pointer-events-none absolute end-3 top-1/2 size-4 -translate-y-1/2 text-[#5F6368]"
              aria-hidden="true"
            />
            <Input
              id="register-email"
              type="email"
              dir="ltr"
              autoComplete="email"
              placeholder="البريد الإلكتروني"
              className="h-10 pe-9 text-end"
              aria-invalid={Boolean(fieldErrors.email)}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
          {fieldErrors.email ? <p className="text-xs text-destructive">{fieldErrors.email}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="register-password" className="sr-only">
            كلمة المرور
          </Label>
          <div className="relative">
            <Lock
              className="pointer-events-none absolute start-3 top-1/2 size-4 -translate-y-1/2 text-[#5F6368]"
              aria-hidden="true"
            />
            <Input
              id="register-password"
              type={showPassword ? "text" : "password"}
              dir="ltr"
              autoComplete="new-password"
              placeholder="كلمة المرور"
              className="h-10 ps-9 pe-9 text-end"
              aria-invalid={Boolean(fieldErrors.password)}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
            <button
              type="button"
              onClick={() => setShowPassword((value) => !value)}
              aria-label={showPassword ? "إخفاء كلمة المرور" : "إظهار كلمة المرور"}
              className="absolute end-3 top-1/2 -translate-y-1/2 text-[#5F6368] transition-colors hover:text-[#161616]"
            >
              {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            </button>
          </div>
          {fieldErrors.password ? (
            <p className="text-xs text-destructive">{fieldErrors.password}</p>
          ) : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="register-confirm-password" className="sr-only">
            تأكيد كلمة المرور
          </Label>
          <div className="relative">
            <Lock
              className="pointer-events-none absolute start-3 top-1/2 size-4 -translate-y-1/2 text-[#5F6368]"
              aria-hidden="true"
            />
            <Input
              id="register-confirm-password"
              type={showConfirmPassword ? "text" : "password"}
              dir="ltr"
              autoComplete="new-password"
              placeholder="تأكيد كلمة المرور"
              className="h-10 ps-9 pe-9 text-end"
              aria-invalid={Boolean(fieldErrors.confirmPassword)}
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword((value) => !value)}
              aria-label={showConfirmPassword ? "إخفاء تأكيد كلمة المرور" : "إظهار تأكيد كلمة المرور"}
              className="absolute end-3 top-1/2 -translate-y-1/2 text-[#5F6368] transition-colors hover:text-[#161616]"
            >
              {showConfirmPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            </button>
          </div>
          {fieldErrors.confirmPassword ? (
            <p className="text-xs text-destructive">{fieldErrors.confirmPassword}</p>
          ) : null}
        </div>

        {formError ? <p className="text-sm text-destructive">{formError}</p> : null}

        <Button type="submit" className="h-10 w-full" disabled={register.isPending}>
          {register.isPending ? "جاري إنشاء الحساب..." : "إنشاء حساب"}
        </Button>
      </form>
    </div>
  );
}
