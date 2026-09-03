import { apiClient } from "@/lib/api/client";
import type { TranscriptionResponse } from "../types/transcription";

export const textExtractApi = {
  extractAudio: (file: File): Promise<TranscriptionResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<TranscriptionResponse>("/api/text-extract/audio", formData);
  },
};
