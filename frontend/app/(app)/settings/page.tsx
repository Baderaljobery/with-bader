import { Settings } from "lucide-react";

import { PageHeader } from "@/components/shared/page-header";
import { PlaceholderPage } from "@/components/shared/placeholder-page";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="الإعدادات" description="إدارة تفضيلات مساحة العمل والحساب." />
      <PlaceholderPage
        icon={Settings}
        title="الإعدادات ستتوفر قريبًا"
        description="إعدادات مساحة العمل والحساب ستكون هنا."
      />
    </div>
  );
}
