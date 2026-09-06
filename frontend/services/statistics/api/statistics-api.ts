import { apiClient } from "@/lib/api/client";
import type { StatisticsOverview } from "../types/statistics";

export const statisticsApi = {
  getOverview: (): Promise<StatisticsOverview> => apiClient.get<StatisticsOverview>("/api/statistics/overview"),
};
