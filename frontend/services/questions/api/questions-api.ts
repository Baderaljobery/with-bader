import { apiClient } from "@/lib/api/client";
import type {
  GeneratedQuestion,
  Question,
  QuestionCreateInput,
  QuestionGenerationRequest,
  QuestionGenerationResponse,
  QuestionGenerationSaveResponse,
  QuestionImprovementPreview,
  QuestionImprovementRequest,
  QuestionUpdateInput,
  QuestionVersion,
} from "../types/question";

export const questionsApi = {
  list: (guestId: string): Promise<Question[]> =>
    apiClient.get<Question[]>(`/api/guests/${guestId}/questions`),

  create: (guestId: string, input: QuestionCreateInput): Promise<Question> =>
    apiClient.post<Question>(`/api/guests/${guestId}/questions`, input),

  update: (questionId: string, input: QuestionUpdateInput): Promise<Question> =>
    apiClient.patch<Question>(`/api/questions/${questionId}`, input),

  remove: (questionId: string): Promise<void> =>
    apiClient.delete<void>(`/api/questions/${questionId}`),

  listVersions: (questionId: string): Promise<QuestionVersion[]> =>
    apiClient.get<QuestionVersion[]>(`/api/questions/${questionId}/versions`),

  generate: (
    guestId: string,
    request: QuestionGenerationRequest,
  ): Promise<QuestionGenerationResponse> =>
    apiClient.post<QuestionGenerationResponse>(`/api/guests/${guestId}/questions/generate`, request),

  saveGenerated: (
    guestId: string,
    questions: GeneratedQuestion[],
  ): Promise<QuestionGenerationSaveResponse> =>
    apiClient.post<QuestionGenerationSaveResponse>(
      `/api/guests/${guestId}/questions/generated/save`,
      { questions },
    ),

  improve: (
    questionId: string,
    request?: QuestionImprovementRequest,
  ): Promise<QuestionImprovementPreview> =>
    apiClient.post<QuestionImprovementPreview>(`/api/questions/${questionId}/improve`, request ?? {}),

  acceptImprovement: (questionId: string, improvedText: string): Promise<Question> =>
    apiClient.post<Question>(`/api/questions/${questionId}/improve/accept`, {
      improved_text: improvedText,
    }),
};
