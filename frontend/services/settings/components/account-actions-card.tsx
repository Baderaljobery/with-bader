"use client";

import { LogOut, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLogout } from "@/services/auth/hooks/use-logout";
import { DeleteAccountDialog } from "./delete-account-dialog";

export function AccountActionsCard() {
  const logout = useLogout();
  const [deleteOpen, setDeleteOpen] = useState(false);

  function handleLogout() {
    logout.mutate(undefined, {
      onSuccess: () => toast.success("تم تسجيل الخروج"),
      onError: () => toast.error("تعذر تسجيل الخروج، حاول مرة أخرى."),
    });
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>الحساب</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-col gap-3 rounded-xl border border-border p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium text-foreground">تسجيل الخروج</p>
              <p className="text-xs text-muted-foreground">إنهاء الجلسة الحالية والعودة إلى صفحة الدخول.</p>
            </div>
            <Button type="button" variant="outline" onClick={handleLogout} disabled={logout.isPending}>
              <LogOut className="size-4" />
              {logout.isPending ? "جاري تسجيل الخروج..." : "تسجيل الخروج"}
            </Button>
          </div>

          <div className="flex flex-col gap-3 rounded-xl border border-destructive/20 bg-destructive/5 p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium text-destructive">حذف كافة بيانات الحساب</p>
              <p className="text-xs text-muted-foreground">
                إجراء دائم يحذف جميع البيانات المرتبطة بحسابك ولا يمكن التراجع عنه.
              </p>
            </div>
            <Button type="button" variant="destructive" onClick={() => setDeleteOpen(true)}>
              <Trash2 className="size-4" />
              حذف كافة البيانات
            </Button>
          </div>
        </CardContent>
      </Card>

      <DeleteAccountDialog open={deleteOpen} onOpenChange={setDeleteOpen} />
    </>
  );
}
