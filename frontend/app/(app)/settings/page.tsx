import { PageHeader } from "@/components/shared/page-header";
import { AccountActionsCard } from "@/services/settings/components/account-actions-card";
import { AccountInfoCard } from "@/services/settings/components/account-info-card";
import { AppearanceCard } from "@/services/settings/components/appearance-card";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="الإعدادات" description="إدارة حسابك وتفضيلات التطبيق." />

      <div className="mx-auto w-full max-w-2xl space-y-6">
        <AccountInfoCard />
        <AccountActionsCard />
        <AppearanceCard />
      </div>
    </div>
  );
}
