"use client";

import { ErrorState } from "@/components/shared/error-state";
import { PageHeader } from "@/components/shared/page-header";
import { StatisticsOverview } from "@/services/statistics/components/statistics-overview";
import { StatisticsSkeleton } from "@/services/statistics/components/statistics-skeleton";
import { useStatisticsOverview } from "@/services/statistics/hooks/use-statistics-overview";

export default function StatisticsPage() {
  const { data, isPending, isError, refetch } = useStatisticsOverview();

  return (
    <div className="space-y-6">
      <PageHeader title="الإحصائيات" description="تابع نشاط مساحة العمل والتقدّم فيها." />

      {isPending ? (
        <StatisticsSkeleton />
      ) : isError ? (
        <ErrorState description="تعذر تحميل الإحصائيات." onRetry={() => refetch()} />
      ) : (
        <StatisticsOverview data={data} />
      )}
    </div>
  );
}
