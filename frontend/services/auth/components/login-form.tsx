"use client";

import { Eye, EyeOff, Lock, Mail } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { FormEvent } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLogin } from "../hooks/use-login";
import { mapLoginError } from "../lib/error-messages";

export function LoginForm() {
  const router = useRouter();
  const login = useLogin();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    // A fast double-click/double-Enter can fire two submit events before
    // React re-renders the button as disabled - this guard closes that
    // window so one submit can never produce two login requests.
    if (login.isPending) return;
    setError(null);

    login.mutate(
      { email, password },
      {
        onSuccess: () => {
          toast.success("تم تسجيل الدخول بنجاح");
          // replace (not push) so Back can't return to /login once
          // authenticated; refresh re-evaluates proxy.ts and any
          // server-rendered segments against the now-set session cookie.
          router.replace("/");
          router.refresh();
        },
        onError: (err) => setError(mapLoginError(err)),
      },
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1 text-center">
        <h1 className="font-heading text-lg font-semibold text-[#161616]">تسجيل الدخول</h1>
        <p className="text-sm text-[#5F6368]">أدخل بياناتك للوصول إلى لوحة التحكم.</p>
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
              dir="ltr"
              required
              autoComplete="email"
              placeholder="البريد الإلكتروني"
              className="h-10 pe-9 text-end"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="login-password" className="sr-only">
            كلمة المرور
          </Label>
          <div className="relative">
            <Lock
              className="pointer-events-none absolute start-3 top-1/2 size-4 -translate-y-1/2 text-[#5F6368]"
              aria-hidden="true"
            />
            <Input
              id="login-password"
              type={showPassword ? "text" : "password"}
              dir="ltr"
              required
              autoComplete="current-password"
              placeholder="كلمة المرور"
              className="h-10 ps-9 pe-9 text-end"
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
        </div>

        {error ? <p className="text-sm text-destructive">{error}</p> : null}

        <Button type="submit" className="h-10 w-full" disabled={login.isPending}>
          {login.isPending ? "جاري تسجيل الدخول..." : "تسجيل الدخول"}
        </Button>
      </form>
    </div>
  );
}
