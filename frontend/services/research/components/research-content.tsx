import { AchievementsSection } from "./sections/achievements-section";
import { CareerHistorySection } from "./sections/career-history-section";
import { EducationSection } from "./sections/education-section";
import { InterestingEventsSection } from "./sections/interesting-events-section";
import { InterviewAnglesSection } from "./sections/interview-angles-section";
import { ProjectsSection } from "./sections/projects-section";
import { PublicAppearancesSection } from "./sections/public-appearances-section";
import { RoleSummarySection } from "./sections/role-summary-section";
import { SourcesSection } from "./sections/sources-section";
import { TopicsSection } from "./sections/topics-section";
import { IdentityConfirmationBanner } from "./identity-confirmation-banner";
import type { GuestResearch } from "../types/research";

type ResearchContentProps = {
  research: GuestResearch;
  guestJobTitle: string | null;
  guestCompany: string | null;
};

export function ResearchContent({ research, guestJobTitle, guestCompany }: ResearchContentProps) {
  return (
    <div className="space-y-4">
      <IdentityConfirmationBanner identityConfidence={research.identity_confidence} />
      <RoleSummarySection
        roleTitle={research.role_title}
        company={research.company}
        guestJobTitle={guestJobTitle}
        guestCompany={guestCompany}
      />
      <CareerHistorySection items={research.career_history} />
      <EducationSection items={research.education} />
      <AchievementsSection items={research.achievements} />
      <ProjectsSection items={research.projects} />
      <TopicsSection topics={research.topics} />
      <PublicAppearancesSection items={research.public_appearances} />
      <InterestingEventsSection items={research.interesting_events} />
      <InterviewAnglesSection items={research.potential_interview_angles} />
      <SourcesSection sources={research.sources} />
    </div>
  );
}
