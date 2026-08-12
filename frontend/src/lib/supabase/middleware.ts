import { createServerClient } from "@supabase/ssr";
import { type NextRequest, NextResponse } from "next/server";

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey) {
    return response;
  }

  const supabase = createServerClient(url, anonKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet: { name: string; value: string; options?: Record<string, unknown> }[]) {
        cookiesToSet.forEach(({ name, value }) => {
          request.cookies.set(name, value);
        });
        response = NextResponse.next({
          request: {
            headers: request.headers,
          },
        });
        cookiesToSet.forEach(({ name, value, options }) => {
          response.cookies.set(name, value, options);
        });
      },
    },
  });

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const path = request.nextUrl.pathname;

  // Hide living design pages outside local/dev.
  if (
    path.startsWith("/design") &&
    process.env.NODE_ENV === "production" &&
    process.env.NEXT_PUBLIC_ENABLE_DESIGN !== "1"
  ) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  const isProtected =
    path.startsWith("/subjects") ||
    path.startsWith("/onboarding") ||
    path.startsWith("/reset-password");
  const isAuthRoute = path.startsWith("/login");

  if (user && isAuthRoute) {
    return NextResponse.redirect(new URL("/subjects", request.url));
  }

  if (!user && isProtected) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", path);
    return NextResponse.redirect(login);
  }

  return response;
}
