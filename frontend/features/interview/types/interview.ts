import type { AnswerSource, AnswerStatus } from "@/features/questions/types/question";

/**
 * Mirrors backend/app/schemas/guest_transcript.py and guest_interview.py
 * exactly. Question/AnswerStatus/AnswerSource are reused from the Questions
 * feature (same backend QuestionResponse) - not redefined here.
 */

export type GuestTranscript = {
  id: string;
  guest_id: string;
  text: string;
  stt_provider: string | null;
  stt_model: string | null;
  created_at: string;
  updated_at: string;
};

/**
 * The slim, ephemeral shape returned by /transcribe-interview and
 * /match-answers. For an "uncertain" outcome, `answer`/`spoken_question` may
 * be a candidate that was deliberately NOT persisted (see
 * app/interview_intelligence/service.py) - only available from this direct
 * mutation response, never recoverable after a refresh.
 */
export type QuestionAnswerState = {
  question_id: string;
  question: string;
  spoken_question: string | null;
  answer: string | null;
  answer_status: AnswerStatus;
  answer_source: AnswerSource | null;
  confidence: number | null;
};

export type GuestInterviewMatchResponse = {
  guest_id: string;
  transcript: GuestTranscript;
  questions: QuestionAnswerState[];
};

export type QuestionAnswerUpdateInput = {
  answer: string | null;
  spoken_question?: string | null;
};
