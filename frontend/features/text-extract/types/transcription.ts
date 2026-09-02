/**
 * Mirrors backend/app/schemas/transcription.py exactly. This endpoint is
 * stateless - no id, no guest_id, no created_at - the response is the only
 * thing that outlives the request.
 */
export type TranscriptionResponse = {
  text: string;
  provider: string;
  model: string;
  language: string | null;
  duration_seconds: number | null;
};
