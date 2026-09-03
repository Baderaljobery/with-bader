import { BarChart3 } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { PlaceholderPage } from "@/components/shared/placeholder-page";

export default function StatisticsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="الإحصائيات" description="تابع نشاط مساحة العمل والتقدّم فيها." />
      <PlaceholderPage
        icon={BarChart3}
        title="الإحصائيات ستتوفر قريبًا"
        description="ستجد هنا رؤى حول الاستخدام والتقدّم عبر جميع ضيوفك."
      />
    </div>
  );
}
