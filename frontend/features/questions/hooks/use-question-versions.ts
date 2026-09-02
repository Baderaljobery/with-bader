import { useQuery } from "@tanstack/react-query";

import { questionsApi } from "../api/questions-api";
import { questionKeys } from "./query-keys";

export function useQuestionVersions(questionId: string | null) {
  return useQuery({
    queryKey: questionKeys.versions(questionId ?? "none"),
    queryFn: () => questionsApi.listVersions(questionId as string),
    enabled: Boolean(questionId),
  });
}
