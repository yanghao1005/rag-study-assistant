"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/lib/store/authStore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BookOpen, Loader2, ArrowRight, BrainCircuit } from "lucide-react";
import { toast } from "sonner";

export default function AuthPage() {
  const router = useRouter();
  const { signIn, signUp } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleAuth = async (action: 'login' | 'signup') => {
    if (!email || !password) {
      toast.error("Please fill in all fields.");
      return;
    }

    setIsLoading(true);
    try {
      if (action === 'signup') {
        const { error } = await signUp(email, password);
        if (error) throw error;
        toast.success("Check your email to confirm your account!");
      } else {
        const { error } = await signIn(email, password);
        if (error) throw error;
        toast.success("Logged in successfully!");
        router.push("/dashboard");
        router.refresh();
      }
    } catch (error: any) {
      toast.error(error.message || "An error occurred during authentication.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left: Auth Form */}
      <div className="flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-sm space-y-8">
          <div className="flex flex-col space-y-2 text-center lg:text-left">
            <Link href="/" className="inline-flex items-center gap-2 font-bold text-2xl text-primary self-center lg:self-start">
              <BookOpen className="h-6 w-6" />
              <span>SmartStudy AI</span>
            </Link>
            <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
            <p className="text-muted-foreground">Sign in to your account to continue learning.</p>
          </div>

          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-4">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>
            
            <TabsContent value="login">
              <form onSubmit={(e) => { e.preventDefault(); handleAuth('login'); }} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    placeholder="name@example.com" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="password">Password</Label>
                    <Link href="#" className="text-sm font-medium text-primary hover:underline">
                      Forgot password?
                    </Link>
                  </div>
                  <Input 
                    id="password" 
                    type="password" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
                <Button className="w-full" type="submit" disabled={isLoading}>
                  {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ArrowRight className="mr-2 h-4 w-4" />}
                  Sign In
                </Button>
              </form>
            </TabsContent>
            
            <TabsContent value="signup">
              <form onSubmit={(e) => { e.preventDefault(); handleAuth('signup'); }} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="signup-email">Email</Label>
                  <Input 
                    id="signup-email" 
                    type="email" 
                    placeholder="name@example.com" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="signup-password">Password</Label>
                  <Input 
                    id="signup-password" 
                    type="password" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={6}
                  />
                  <p className="text-xs text-muted-foreground">Must be at least 6 characters long.</p>
                </div>
                <Button className="w-full" type="submit" disabled={isLoading}>
                  {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  Create Account
                </Button>
              </form>
            </TabsContent>
          </Tabs>

          <p className="text-center text-sm text-muted-foreground">
            By clicking continue, you agree to our{" "}
            <Link href="/terms" className="underline underline-offset-4 hover:text-primary">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="/privacy" className="underline underline-offset-4 hover:text-primary">
              Privacy Policy
            </Link>
            .
          </p>
        </div>
      </div>

      {/* Right: Feature Showcase (Hidden on mobile) */}
      <div className="hidden lg:flex flex-col bg-muted/30 p-10 text-white dark:text-foreground relative overflow-hidden">
        <div className="absolute inset-0 bg-zinc-900" />
        <div className="relative z-10 flex flex-col items-start justify-center h-full max-w-lg mx-auto space-y-6">
           <div className="space-y-2">
             <h2 className="text-3xl font-bold leading-tight tracking-tighter sm:text-4xl text-white">
                Turn your documents into interactive study guides
             </h2>
             <p className="text-zinc-400 text-lg">
                Upload PDFs, notes, or slides and let our AI create quizzes, flashcards, and summaries instantly.
             </p>
           </div>
           
           <div className="grid grid-cols-2 gap-4 w-full pt-8">
              <div className="p-4 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm">
                <BrainCircuit className="h-6 w-6 text-blue-400 mb-2" />
                <h3 className="font-semibold text-white">AI Analysis</h3>
                <p className="text-sm text-zinc-400">Deep understanding of your content context</p>
              </div>
              <div className="p-4 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm">
                <BookOpen className="h-6 w-6 text-purple-400 mb-2" />
                <h3 className="font-semibold text-white">Smart Quizzes</h3>
                <p className="text-sm text-zinc-400">Adaptive testing to maximize retention</p>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
