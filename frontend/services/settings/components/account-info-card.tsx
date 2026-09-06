"use client";

import { ErrorState } from "@/components/shared/error-state";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCurrentUser } from "@/services/auth/hooks/use-current-user";

function InfoRow({ label, value, ltr }: { label: string; value: string; ltr?: boolean }) {
  return (
    <div className="flex flex-col gap-1 border-b border-border/70 py-3 last:border-b-0 sm:flex-row sm:items-center sm:justify-between">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-medium text-foreground" dir={ltr ? "ltr" : undefined}>
        {value}
      </span>
    </div>
  );
}

export function AccountInfoCard() {
  const { data: user, isPending, isError, refetch } = useCurrentUser();

  return (
    <Card>
      <CardHeader>
        <CardTitle>معلومات الحساب</CardTitle>
      </CardHeader>
      <CardContent>
        {isPending ? (
          <div className="space-y-3 py-1">
            <Skeleton className="h-5 w-full" />
            <Skeleton className="h-5 w-full" />
          </div>
        ) : isError || !user ? (
          <ErrorState description="تعذر تحميل معلومات الحساب." onRetry={() => refetch()} />
        ) : (
          <div>
            <InfoRow label="اسم المستخدم" value={user.name} />
            <InfoRow label="البريد الإلكتروني" value={user.email} ltr />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
