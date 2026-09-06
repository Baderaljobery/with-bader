/** Mirrors backend/app/schemas/statistics.py exactly. */
export type StatisticsTotals = {
  guests: number;
  scheduled_interviews: number;
  completed_interviews: number;
  questions: number;
  content_drafts: number;
  approved_content: number;
  designs: number;
  design_slides: number;
};

export type PlatformCount = {
  platform: "linkedin" | "x" | "instagram" | "general";
  count: number;
};

export type ActivityPoint = {
  /** "YYYY-MM-DD" */
  date: string;
  count: number;
};

export type StatisticsOverview = {
  totals: StatisticsTotals;
  content_by_platform: PlatformCount[];
  activity: ActivityPoint[];
};
