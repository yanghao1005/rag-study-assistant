import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, BookOpen, BrainCircuit, FileText, Sparkles, CheckCircle2 } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2 font-bold text-xl text-primary">
            <BookOpen className="h-6 w-6" />
            <span>SmartStudy AI</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-sm font-medium hover:underline underline-offset-4">
              Access Dashboard
            </Link>
            <Button asChild size="sm">
              <Link href="/dashboard">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="space-y-6 pb-8 pt-6 md:pb-12 md:pt-10 lg:py-32">
          <div className="container mx-auto flex max-w-[64rem] flex-col items-center gap-4 text-center">
            <div className="rounded-2xl bg-muted px-4 py-1.5 text-sm font-medium">
              🚀 The RAG-powered study assistant is here
            </div>
            <h1 className="font-heading text-3xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight">
              Master any subject with <span className="text-primary">AI intelligence</span>
            </h1>
            <p className="max-w-[42rem] leading-normal text-muted-foreground sm:text-xl sm:leading-8">
              Upload your textbooks and notes. Let our AI generate flashcards, quizzes, and summaries tailored exactly to your source material.
            </p>
            <div className="space-x-4">
              <Button asChild size="lg" className="h-12 px-8 text-lg">
                <Link href="/dashboard">
                  Start Learning Now <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="h-12 px-8 text-lg">
                How it works
              </Button>
            </div>
          </div>
        </section>

        {/* Feature Grid */}
        <section className="container mx-auto space-y-6 bg-slate-50 py-8 dark:bg-transparent md:py-12 lg:py-24 rounded-3xl my-8">
          <div className="mx-auto flex max-w-[58rem] flex-col items-center space-y-4 text-center">
            <h2 className="font-heading text-3xl leading-[1.1] sm:text-3xl md:text-6xl font-bold">
              Features
            </h2>
            <p className="max-w-[85%] leading-normal text-muted-foreground sm:text-lg sm:leading-7">
              Everything you need to transform passive reading into active learning.
            </p>
          </div>
          <div className="mx-auto grid justify-center gap-4 sm:grid-cols-2 md:max-w-[64rem] md:grid-cols-3">
            <div className="relative overflow-hidden rounded-lg border bg-background p-2">
              <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                <FileText className="h-12 w-12 text-primary" />
                <div className="space-y-2">
                  <h3 className="font-bold">Document Analysis</h3>
                  <p className="text-sm text-muted-foreground">
                    Upload PDFs and let our RAG system extract key concepts automatically.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background p-2">
              <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                <BrainCircuit className="h-12 w-12 text-primary" />
                <div className="space-y-2">
                  <h3 className="font-bold">AI Flashcards</h3>
                  <p className="text-sm text-muted-foreground">
                    Generate flipped cards for efficient memorization of definitions and terms.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background p-2">
              <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                <Sparkles className="h-12 w-12 text-primary" />
                <div className="space-y-2">
                  <h3 className="font-bold">Smart Quizzes</h3>
                  <p className="text-sm text-muted-foreground">
                    Test your knowledge with multiple choice questions and instant explanations.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Steps Section */}
        <section className="container mx-auto py-8 md:py-12 lg:py-24">
            <div className="grid gap-12 lg:grid-cols-2 items-center">
                 <div className="space-y-6">
                    <h2 className="text-3xl font-bold md:text-4xl">How SmartStudy Works</h2>
                    <p className="text-lg text-muted-foreground">
                        Our platform uses Retrieval-Augmented Generation (RAG) to ensure every question and flashcard is grounded in your actual course material.
                    </p>
                    <ul className="space-y-4">
                        <li className="flex items-center gap-3">
                            <CheckCircle2 className="h-6 w-6 text-green-500" />
                            <span className="font-medium">1. Create a Topic & Upload PDFs</span>
                        </li>
                        <li className="flex items-center gap-3">
                            <CheckCircle2 className="h-6 w-6 text-green-500" />
                            <span className="font-medium">2. AI Indexes your content</span>
                        </li>
                        <li className="flex items-center gap-3">
                            <CheckCircle2 className="h-6 w-6 text-green-500" />
                            <span className="font-medium">3. Generate unlimited study aids</span>
                        </li>
                    </ul>
                 </div>
                 <div className="rounded-xl border bg-muted/50 p-8 h-[400px] flex items-center justify-center">
                    {/* Placeholder for Product Screenshot */}
                    <div className="text-center space-y-4">
                        <BookOpen className="h-24 w-24 text-muted-foreground mx-auto opacity-20" />
                        <p className="text-muted-foreground font-medium">Interactive Demo Preview</p>
                    </div>
                 </div>
            </div>
        </section>
      </main>
      
      <footer className="border-t py-6 md:py-0">
        <div className="container mx-auto flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <div className="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
            <BookOpen className="h-6 w-6" />
            <p className="text-center text-sm leading-loose md:text-left">
              Built by <span className="font-medium underline underline-offset-4">SmartStudy AI</span>.
              The source code is available on <span className="font-medium underline underline-offset-4">GitHub</span>.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}