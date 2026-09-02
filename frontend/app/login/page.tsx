"use client";

import { Eye, EyeOff, Lock, Mail } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";

import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    toast.info("تسجيل الدخول غير مفعّل بعد في هذه النسخة.");
  }

  return (
    <div className="flex min-h-dvh items-center justify-center bg-[#F7F8FA] px-4 py-10">
      <div className="w-full max-w-sm space-y-6 rounded-2xl border border-[#E6EAF0] bg-white p-8 shadow-[0_1px_2px_rgba(22,22,22,0.04),0_12px_32px_-16px_rgba(27,143,234,0.18)]">
        <div className="flex flex-col items-center gap-4 text-center">
          <Logo size="lg" />
          <div className="space-y-1">
            <h1 className="font-heading text-lg font-semibold text-[#161616]">تسجيل الدخول</h1>
            <p className="text-sm text-[#5F6368]">أدخل بياناتك للوصول إلى لوحة التحكم.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="login-email" className="sr-only">
              البريد الإلكتروني
            </Label>
            <div className="relative">
              <Mail
                className="pointer-events-none absolute end-3 top-1/2 size-4 -translate-y-1/2 text-[#5F6368]"
                aria-hidden="true"
              />
              <Input
                id="login-email"
                type="email"
                required
                autoComplete="email"
                placeholder="البريد الإلكتروني"
                className="h-10 pe-9"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="login-password" className="sr-only">
              كلمة المرور
            </Label>
            <div className="relative">
              <Lock
                className="pointer-events-none absolute end-3 top-1/2 size-4 -translate-y-1/2 text-[#5F6368]"
                aria-hidden="true"
              />
              <Input
                id="login-password"
                type={showPassword ? "text" : "password"}
                required
                autoComplete="current-password"
                placeholder="كلمة المرور"
                className="h-10 ps-9 pe-9"
              />
              <button
                type="button"
                onClick={() => setShowPassword((value) => !value)}
                aria-label={showPassword ? "إخفاء كلمة المرور" : "إظهار كلمة المرور"}
                className="absolute start-3 top-1/2 -translate-y-1/2 text-[#5F6368] transition-colors hover:text-[#161616]"
              >
                {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
              </button>
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm text-[#5F6368]">
            <Checkbox name="remember" />
            تذكرني
          </label>

          <Button type="submit" className="w-full">
            تسجيل الدخول
          </Button>
        </form>

        <div className="text-center">
          <a href="#" className="text-sm font-medium text-[#1B8FEA] hover:underline">
            نسيت كلمة المرور؟
          </a>
        </div>
      </div>
    </div>
  );
}
