"use client";

import { useEffect } from "react";

import { ErrorState } from "@/components/shared/error-state";

export default function GlobalErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <ErrorState
        title="حدث خطأ غير متوقع"
        description="حاول مرة أخرى، وإذا استمرت المشكلة فحاول تحديث الصفحة."
        onRetry={reset}
      />
    </div>
  );
}
