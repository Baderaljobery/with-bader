import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { AUTH_COOKIE_NAME } from "@/lib/auth/constants";

/**
 * Route guard for every private page (guests, calendar, statistics,
 * settings, text-extract, home) vs. the public /login page.
 *
 * This is an *optimistic* check (cookie presence only, never signature
 * verification - the frontend never holds the JWT secret) that runs
 * before any page renders, so an unauthenticated visitor is redirected to
 * /login without ever seeing a flash of private content, and a logged-in
 * visitor never sees the login form. It is a UX guard, not the security
 * boundary - every protected API route independently verifies the session
 * and enforces per-user data ownership on the backend regardless of what
 * this proxy decides.
 */
export function proxy(request: NextRequest) {
  const hasSessionCookie = request.cookies.has(AUTH_COOKIE_NAME);
  const isLoginRoute = request.nextUrl.pathname === "/login";

  if (!hasSessionCookie && !isLoginRoute) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (hasSessionCookie && isLoginRoute) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|logo-full.png|logo-icon.png).*)"],
};
