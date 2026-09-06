import { useMutation } from "@tanstack/react-query";

import { textExtractApi } from "../api/text-extract-api";

/**
 * No query cache here on purpose - POST /api/text-extract/audio is
 * stateless and nothing is persisted, so the result only ever lives in the
 * calling page's own state for as long as it's open.
 */
export function useAudioTextExtract() {
  return useMutation({
    mutationFn: (file: File) => textExtractApi.extractAudio(file),
  });
}
