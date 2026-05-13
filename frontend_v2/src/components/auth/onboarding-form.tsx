"use client";

import { useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSessionStore } from "@/features/auth/session-store";
import { getSupabaseBrowserClient } from "@/lib/supabase/client";

function resolveNextPath(raw: string | null): string {
  if (!raw || !raw.startsWith("/")) {
    return "/dashboard";
  }
  return raw;
}

export function OnboardingForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = resolveNextPath(searchParams.get("next"));

  const { token, userEmail } = useSessionStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState<"signin" | "signup" | null>(null);

  const isSignedIn = Boolean(token);

  const passwordHint = useMemo(() => {
    if (password.length >= 8) {
      return "Password length looks good.";
    }
    return "Use at least 8 characters.";
  }, [password.length]);

  const handleSignIn = async () => {
    if (!email.trim() || !password) {
      toast.error("Email and password are required.");
      return;
    }

    setBusy("signin");
    try {
      const supabase = getSupabaseBrowserClient();
      const { error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (error) {
        throw error;
      }

      toast.success("Signed in successfully.");
      router.replace(nextPath);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Sign-in failed.");
    } finally {
      setBusy(null);
    }
  };

  const handleSignUp = async () => {
    if (!email.trim() || !password) {
      toast.error("Email and password are required.");
      return;
    }

    setBusy("signup");
    try {
      const supabase = getSupabaseBrowserClient();
      const { error } = await supabase.auth.signUp({
        email: email.trim(),
        password,
      });

      if (error) {
        throw error;
      }

      toast.success("Account created. Check your email if confirmation is required, then sign in.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Sign-up failed.");
    } finally {
      setBusy(null);
    }
  };

  const handleContinue = () => {
    router.replace(nextPath);
  };

  return (
    <main className="mx-auto grid min-h-screen w-full max-w-5xl place-items-center bg-[var(--sl-base)] px-4 py-10">
      <Card className="w-full max-w-2xl border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <Badge className="w-fit">Supabase Authentication</Badge>
          <CardTitle className="text-2xl text-[var(--sl-text-primary)]">Sign in to your study workspace</CardTitle>
          <CardDescription className="text-[var(--sl-text-secondary)]">
            The app now uses Supabase Auth to obtain bearer tokens automatically. No manual token pasting is needed.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-5">
          {isSignedIn ? (
            <div className="grid gap-3 rounded-sl-soft border border-[var(--sl-muted)] bg-[var(--sl-base)] p-4">
              <p className="text-sm">
                Signed in as <span className="font-medium">{userEmail || "authenticated user"}</span>
              </p>
              <div className="flex flex-wrap gap-2">
                <Button onClick={handleContinue} className="rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]">Continue to workspace</Button>
              </div>
            </div>
          ) : null}

          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
            />
            <p className="text-xs text-muted-foreground">{passwordHint}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button type="button" onClick={handleSignIn} disabled={busy !== null} className="rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]">
              {busy === "signin" ? "Signing in..." : "Sign In"}
            </Button>
            <Button type="button" variant="secondary" onClick={handleSignUp} disabled={busy !== null} className="rounded-sl-standard">
              {busy === "signup" ? "Creating account..." : "Sign Up"}
            </Button>
            <p className="self-center text-xs text-muted-foreground">Next route: {nextPath}</p>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
