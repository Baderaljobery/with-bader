"use client";

import { CalendarClock, FileText, HelpCircle, LayoutTemplate, Users } from "lucide-react";

import { ActivityTrendCard } from "./activity-trend-card";
import { DualStatCard } from "./dual-stat-card";
import { MetricCard } from "./metric-card";
import { PlatformBreakdownCard } from "./platform-breakdown-card";
import type { StatisticsOverview as StatisticsOverviewData } from "../types/statistics";

const TALL_CARD_HEIGHT = "h-[300px] lg:h-[340px]";

type StatisticsOverviewProps = {
  data: StatisticsOverviewData;
};

export function StatisticsOverview({ data }: StatisticsOverviewProps) {
  const { totals, content_by_platform, activity } = data;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <MetricCard
          tone="navy"
          icon={Users}
          title="الضيوف"
          value={totals.guests}
          valueLabel="إجمالي الضيوف المضافين"
          secondary={{ icon: HelpCircle, label: "الأسئلة المُعدّة", value: totals.questions }}
          className={`${TALL_CARD_HEIGHT} lg:col-span-1`}
        />
        <ActivityTrendCard activity={activity} className={`${TALL_CARD_HEIGHT} lg:col-span-2`} />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <DualStatCard
          tone="teal"
          icon={CalendarClock}
          title="المقابلات"
          primary={{ label: "مجدولة", value: totals.scheduled_interviews }}
          secondary={{ label: "مكتملة", value: totals.completed_interviews }}
        />
        <DualStatCard
          tone="blue"
          icon={FileText}
          title="المحتوى"
          primary={{ label: "المسودات", value: totals.content_drafts }}
          secondary={{ label: "المعتمد", value: totals.approved_content }}
        />
        <DualStatCard
          tone="neutral"
          icon={LayoutTemplate}
          title="التصاميم"
          primary={{ label: "التصاميم", value: totals.designs }}
          secondary={{ label: "الشرائح", value: totals.design_slides }}
        />
      </div>

      <PlatformBreakdownCard platforms={content_by_platform} />
    </div>
  );
}
