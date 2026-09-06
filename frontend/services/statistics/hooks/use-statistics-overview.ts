import { useQuery } from "@tanstack/react-query";

import { statisticsApi } from "../api/statistics-api";
import { statisticsKeys } from "./query-keys";

export function useStatisticsOverview() {
  return useQuery({
    queryKey: statisticsKeys.overview(),
    queryFn: statisticsApi.getOverview,
  });
}
