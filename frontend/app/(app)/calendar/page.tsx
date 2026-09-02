import { CalendarDays } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { PlaceholderPage } from "@/components/shared/placeholder-page";

export default function CalendarPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="التقويم" description="خطّط لمقابلاتك القادمة وتابعها." />
      <PlaceholderPage
        icon={CalendarDays}
        title="التقويم سيتم تفعيله قريبًا"
        description="أدوات الجدولة والتخطيط للمقابلات ستكون هنا."
      />
    </div>
  );
}
