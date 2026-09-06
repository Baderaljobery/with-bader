/** Must match `auth_cookie_name` / AUTH_COOKIE_NAME in
 * backend/app/core/config.py (and backend/.env) exactly - this is only
 * used to check whether a session cookie is *present* (an optimistic,
 * unsigned check for routing/UX, see proxy.ts), never to read or verify
 * its contents. The frontend never has the JWT signing secret and never
 * needs it - real verification always happens on the backend. */
export const AUTH_COOKIE_NAME = "with_bader_session";
