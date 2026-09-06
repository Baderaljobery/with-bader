const configuredBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

// Host-only cookie footgun: the backend's session cookie has no explicit
// Domain attribute (see backend/app/core/auth.py's set_session_cookie), so
// it is scoped to the exact hostname string of whichever backend URL the
// browser talked to. "localhost" and "127.0.0.1" are two DIFFERENT
// hostnames to a browser's cookie jar even though they resolve to the same
// machine - `next dev` serves the app at http://localhost:3000 by default,
// so if NEXT_PUBLIC_API_BASE_URL points at 127.0.0.1 (or vice versa), the
// session cookie the backend sets is invisible to requests made from the
// page itself (including proxy.ts's cookie check on every navigation).
// The visible symptom is exactly "login succeeds but never redirects in" -
// proxy.ts sees no cookie and bounces straight back to /login.
const LOOPBACK_HOSTS = new Set(["localhost", "127.0.0.1"]);

function resolveApiBaseUrl(): string {
  if (typeof window === "undefined") return configuredBaseUrl;

  const configured = new URL(configuredBaseUrl);
  const pageHostname = window.location.hostname;

  // Only realign the two well-known local-dev loopback spellings onto
  // whichever one the page is actually being viewed from - a real
  // deployed API host (never "localhost"/"127.0.0.1") is left untouched,
  // so this can't affect a production configuration.
  if (LOOPBACK_HOSTS.has(configured.hostname) && LOOPBACK_HOSTS.has(pageHostname)) {
    configured.hostname = pageHostname;
  }

  return configured.origin;
}

export const API_BASE_URL = resolveApiBaseUrl();
