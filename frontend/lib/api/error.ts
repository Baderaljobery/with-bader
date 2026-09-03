/**
 * Normalized error for any failed API call.
 *
 * FastAPI error bodies come in two shapes:
 *   { "detail": "Guest not found" }
 *   { "detail": [{ "loc": [...], "msg": "...", "type": "..." }, ...] }
 *
 * `message` is always a safe, displayable string. `details` keeps the raw
 * validation array (when present) for callers that want field-level errors.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

type FastApiValidationItem = {
  loc?: unknown[];
  msg?: string;
  type?: string;
};

function isValidationArray(value: unknown): value is FastApiValidationItem[] {
  return (
    Array.isArray(value) &&
    value.every((item) => typeof item === "object" && item !== null)
  );
}

export function parseErrorBody(status: number, body: unknown): ApiError {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;

    if (typeof detail === "string") {
      return new ApiError(detail, status, undefined);
    }

    if (isValidationArray(detail)) {
      const message =
        detail
          .map((item) => item.msg)
          .filter((msg): msg is string => Boolean(msg))
          .join(" · ") || "Request validation failed.";
      return new ApiError(message, status, detail);
    }
  }

  return new ApiError("Something went wrong. Please try again.", status, body);
}
