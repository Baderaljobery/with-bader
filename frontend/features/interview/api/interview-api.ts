import { apiClient } from "@/lib/api/client";
import type { Question } from "@/features/questions/types/question";
import type {
  GuestInterviewMatchResponse,
  GuestTranscript,
  QuestionAnswerUpdateInput,
} from "../types/interview";

export const interviewApi = {
  getTranscript: (guestId: string): Promise<GuestTranscript> =>
    apiClient.get<GuestTranscript>(`/api/guests/${guestId}/transcript`),

  updateTranscript: (guestId: string, text: string): Promise<GuestTranscript> =>
    apiClient.patch<GuestTranscript>(`/api/guests/${guestId}/transcript`, { text }),

  transcribe: (
    guestId: string,
    file: File,
    replaceExisting: boolean,
  ): Promise<GuestInterviewMatchResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<GuestInterviewMatchResponse>(
      `/api/guests/${guestId}/transcribe-interview`,
      formData,
      { query: { replace_existing: replaceExisting } },
    );
  },

  matchAnswers: (guestId: string): Promise<GuestInterviewMatchResponse> =>
    apiClient.post<GuestInterviewMatchResponse>(`/api/guests/${guestId}/match-answers`),

  updateQuestionAnswer: (questionId: string, input: QuestionAnswerUpdateInput): Promise<Question> =>
    apiClient.patch<Question>(`/api/questions/${questionId}/answer`, input),
};
