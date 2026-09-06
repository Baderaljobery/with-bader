"use client";

import { AuthShell } from "@/services/auth/components/auth-shell";
import { LoginForm } from "@/services/auth/components/login-form";
import { RegisterForm } from "@/services/auth/components/register-form";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function LoginPage() {
  return (
    <AuthShell>
      <Tabs defaultValue="login" className="gap-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="login">تسجيل الدخول</TabsTrigger>
          <TabsTrigger value="register">إنشاء حساب</TabsTrigger>
        </TabsList>
        <TabsContent value="login">
          <LoginForm />
        </TabsContent>
        <TabsContent value="register">
          <RegisterForm />
        </TabsContent>
      </Tabs>
    </AuthShell>
  );
}
