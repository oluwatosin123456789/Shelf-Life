import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Next.js Middleware — Route Protection
 *
 * Note: We can't access localStorage in middleware (runs on the edge).
 * Instead, we check for a cookie. But since we're using localStorage for
 * token storage (simpler for an MVP), we use a lightweight client-side
 * redirect approach instead.
 *
 * This middleware handles only the basic public/private route split:
 * - Public routes: /, /auth/signin, /auth/signup
 * - Protected routes: everything else
 *
 * For MVP, actual auth checking happens client-side via the AuthProvider.
 * This middleware is a safety net that redirects obviously unauthenticated
 * requests (e.g., direct URL navigation).
 */

// Routes that don't require authentication
const PUBLIC_PATHS = ["/", "/auth/signin", "/auth/signup"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes
  if (PUBLIC_PATHS.includes(pathname)) {
    return NextResponse.next();
  }

  // Allow Next.js internals and static files
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  // For protected routes: check if we have a token cookie
  // Since we use localStorage (not cookies), we add a sync cookie on login
  const token = request.cookies.get("fresco_auth");
  if (!token) {
    const signinUrl = new URL("/auth/signin", request.url);
    signinUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(signinUrl);
  }

  return NextResponse.next();
}

export const config = {
  // Only run on app routes, not static files
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
