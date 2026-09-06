import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type RoleSummarySectionProps = {
  roleTitle: string | null;
  company: string | null;
  guestJobTitle: string | null;
  guestCompany: string | null;
};

export function RoleSummarySection({
  roleTitle,
  company,
  guestJobTitle,
  guestCompany,
}: RoleSummarySectionProps) {
  // Research fields take priority; the guest's own profile fields are a
  // display-only fallback when research didn't determine one - never sent
  // back to the server, never mutates the research record.
  const displayRole = roleTitle ?? guestJobTitle;
  const displayCompany = company ?? guestCompany;

  if (!displayRole && !displayCompany) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>الملخص المهني</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm font-medium text-[#161616]">
          {[displayRole, displayCompany].filter(Boolean).join(" · ")}
        </p>
      </CardContent>
    </Card>
  );
}
