import { API_BASE_URL } from "./config";
import { ApiError, parseErrorBody } from "./error";

type QueryValue = string | number | boolean | undefined | null;

type RequestOptions = {
  query?: Record<string, QueryValue>;
  signal?: AbortSignal;
};

function buildUrl(path: string, query?: Record<string, QueryValue>): string {
  const url = new URL(path.replace(/^\//, ""), `${API_BASE_URL}/`);

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }
  }

  return url.toString();
}

async function request<TResponse>(
  method: "GET" | "POST" | "PATCH" | "DELETE",
  path: string,
  body?: unknown,
  options?: RequestOptions,
): Promise<TResponse> {
  let response: Response;
  // FormData (file uploads) must be sent as-is, with the browser setting its
  // own multipart Content-Type + boundary - never JSON.stringify'd.
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;

  try {
    response = await fetch(buildUrl(path, options?.query), {
      method,
      headers: body !== undefined && !isFormData ? { "Content-Type": "application/json" } : undefined,
      body: body === undefined ? undefined : isFormData ? body : JSON.stringify(body),
      signal: options?.signal,
      // The backend authenticates via an HttpOnly session cookie (never a
      // frontend-visible token) - the browser only attaches it cross-origin
      // (frontend:3000 -> backend:8000) if we ask it to.
      credentials: "include",
    });
  } catch {
    throw new ApiError(
      "Could not reach the server. Check your connection and try again.",
      0,
    );
  }

  if (response.status === 204) {
    return undefined as TResponse;
  }

  const text = await response.text();
  const data = text ? JSON.parse(text) : undefined;

  if (!response.ok) {
    throw parseErrorBody(response.status, data);
  }

  return data as TResponse;
}

export const apiClient = {
  get: <TResponse>(path: string, options?: RequestOptions) =>
    request<TResponse>("GET", path, undefined, options),
  post: <TResponse>(path: string, body?: unknown, options?: RequestOptions) =>
    request<TResponse>("POST", path, body, options),
  patch: <TResponse>(path: string, body?: unknown, options?: RequestOptions) =>
    request<TResponse>("PATCH", path, body, options),
  delete: <TResponse = void>(path: string, options?: RequestOptions) =>
    request<TResponse>("DELETE", path, undefined, options),
};

export { ApiError };
