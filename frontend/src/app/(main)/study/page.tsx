"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ScopeSelector, StudyScope } from "@/components/study/ScopeSelector";
import { FlashcardCarousel } from "@/components/study/FlashcardCarousel";
import { QuizInterface } from "@/components/study/QuizInterface";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { BrainCircuit, BookCopy, Sparkles, ArrowLeft } from "lucide-react";
import { Flashcard, QuizQuestion } from "@/types/models";
import { generateFlashcards, generateQuiz, getGeneratedHistory } from "@/lib/api/study";
import { useAuthStore } from "@/lib/store/authStore";
import { toast } from "sonner";
import { GeneratedHistoryItem } from "@/types/api";

type StudyMode = 'flashcards' | 'quiz';

export default function StudyPage() {
  const searchParams = useSearchParams();
  const defaultSubjectId = searchParams.get('subject') || undefined;
  const user = useAuthStore((state) => state.user);

  const [scope, setScope] = useState<StudyScope | null>(null);
  const [mode, setMode] = useState<StudyMode>('flashcards');
  const [sessionState, setSessionState] = useState<'config' | 'loading' | 'active'>('config');
  const [query, setQuery] = useState('');
  const [count, setCount] = useState(8);
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [history, setHistory] = useState<GeneratedHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  
  // Data State
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);

  useEffect(() => {
    const loadHistory = async () => {
      if (!scope || !user) {
        setHistory([]);
        return;
      }

      const historyScope = scope.mode === 'document' ? 'document' : 'subject';
      const scopeId = scope.mode === 'document' ? scope.documentId : scope.subjectId;
      if (!scopeId) {
        setHistory([]);
        return;
      }

      try {
        setHistoryLoading(true);
        const response = await getGeneratedHistory({
          user_id: user.id,
          scope: historyScope,
          scope_id: scopeId,
          limit: 8,
        });
        setHistory(response.items ?? []);
      } catch {
        setHistory([]);
      } finally {
        setHistoryLoading(false);
      }
    };

    loadHistory();
  }, [scope, user]);

  const handleStartSession = async () => {
    if (!scope || !user) return;
    const cleanQuery = query.trim();
    
    setSessionState('loading');

    const generationScope = scope.mode === 'document' ? 'document' : 'subject';
    const scopeId = scope.mode === 'document' ? scope.documentId : scope.subjectId;

    try {
      if (!scopeId) {
        throw new Error('Invalid study scope');
      }

      if (mode === 'flashcards') {
        const result = await generateFlashcards({
          scope: generationScope,
          scope_id: scopeId,
          ...(cleanQuery ? { query: cleanQuery } : {}),
          user_id: user.id,
          count,
          prompt_profile: 'concise',
          front_max_chars: 90,
          back_max_chars: 220,
          save: true,
          debug: true,
        });
        setFlashcards(result.flashcards);
      } else {
        const result = await generateQuiz({
          scope: generationScope,
          scope_id: scopeId,
          ...(cleanQuery ? { query: cleanQuery } : {}),
          user_id: user.id,
          count,
          difficulty,
          prompt_profile: 'exam',
          question_max_chars: 180,
          explanation_max_chars: 260,
          save: true,
          debug: true,
        });
        setQuizQuestions(result.questions);
      }

      const historyScope = scope.mode === 'document' ? 'document' : 'subject';
      const historyScopeId = scope.mode === 'document' ? scope.documentId : scope.subjectId;
      if (historyScopeId) {
        const historyResponse = await getGeneratedHistory({
          user_id: user.id,
          scope: historyScope,
          scope_id: historyScopeId,
          limit: 8,
        });
        setHistory(historyResponse.items ?? []);
      }

      setSessionState('active');
    } catch (error: any) {
      toast.error(error?.message || 'Failed to generate study content');
      setSessionState('config');
    }
  };

  const resetSession = () => {
    setSessionState('config');
    setFlashcards([]);
    setQuizQuestions([]);
  };

  if (sessionState === 'active') {
    return (
      <div className="container max-w-5xl py-8 space-y-6">
        <Button variant="ghost" onClick={resetSession} className="gap-2 pl-0 hover:pl-2 transition-all">
          <ArrowLeft className="h-4 w-4" />
          Back to Setup
        </Button>
        
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight">
             {mode === 'flashcards' ? 'Flashcard Session' : 'Quiz Session'}
          </h1>
          <div className="text-muted-foreground text-sm">
             Live Mode • Backend v3
          </div>
        </div>

        {mode === 'flashcards' ? (
             <FlashcardCarousel flashcards={flashcards} />
        ) : (
            <QuizInterface 
                questions={quizQuestions} 
                onRetake={() => {
                   // Shuffle logic could go here
                }}
            />
        )}
      </div>
    );
  }

  if (sessionState === 'loading') {
      return (
          <div className="container max-w-5xl py-24 flex flex-col items-center justify-center space-y-4 text-center">
              <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
              <h2 className="text-2xl font-semibold">Generating Content...</h2>
              <p className="text-muted-foreground">Our AI is reading your documents and preparing your {mode}.</p>
          </div>
      );
  }

  return (
    <div className="container max-w-5xl py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-primary flex items-center gap-2">
          <BrainCircuit className="h-8 w-8" />
          Study Integration
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">
          Transform your documents into interactive study materials powered by AI.
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-[1fr_350px]">
        {/* Left Column: Scope Selection */}
        <div className="space-y-6">
           <ScopeSelector onScopeChange={setScope} defaultSubjectId={defaultSubjectId} />

           <Card>
             <CardHeader>
               <CardTitle>Generation Settings</CardTitle>
               <CardDescription>
                 Topic is optional. Leave empty to let the system pick key concepts automatically.
               </CardDescription>
             </CardHeader>
             <CardContent className="space-y-4">
               <div className="space-y-2">
                 <Label htmlFor="query">Topic / Query</Label>
                 <Input
                   id="query"
                   placeholder="e.g. differences between supervised and unsupervised learning"
                   value={query}
                   onChange={(event) => setQuery(event.target.value)}
                 />
                 <p className="text-xs text-muted-foreground">
                   Optional examples: "Porter five forces", "Photosynthesis stages", "TCP vs UDP".
                 </p>
               </div>
               <div className="grid grid-cols-2 gap-4">
                 <div className="space-y-2">
                   <Label htmlFor="count">Count</Label>
                   <Input
                     id="count"
                     type="number"
                     min={1}
                     max={20}
                     value={count}
                     onChange={(event) => setCount(Math.max(1, Math.min(20, Number(event.target.value) || 1)))}
                   />
                 </div>
                 <div className="space-y-2">
                   <Label htmlFor="difficulty">Quiz Difficulty</Label>
                   <Tabs value={difficulty} onValueChange={(value) => setDifficulty(value as 'easy' | 'medium' | 'hard')}>
                     <TabsList className="grid grid-cols-3 w-full">
                       <TabsTrigger value="easy">Easy</TabsTrigger>
                       <TabsTrigger value="medium">Medium</TabsTrigger>
                       <TabsTrigger value="hard">Hard</TabsTrigger>
                     </TabsList>
                   </Tabs>
                 </div>
               </div>
             </CardContent>
           </Card>
           
           <Card className={!scope ? "opacity-50" : ""}>
             <CardHeader>
               <CardTitle>Select Mode</CardTitle>
               <CardDescription>Choose how you want to test your knowledge.</CardDescription>
             </CardHeader>
             <CardContent>
               <Tabs defaultValue="flashcards" value={mode} onValueChange={(v) => setMode(v as any)}>
                 <TabsList className="grid w-full grid-cols-2">
                   <TabsTrigger value="flashcards" className="gap-2 py-3">
                     <BookCopy className="h-4 w-4" />
                     Flashcards
                   </TabsTrigger>
                   <TabsTrigger value="quiz" className="gap-2 py-3">
                     <Sparkles className="h-4 w-4" />
                     Quiz Game
                   </TabsTrigger>
                 </TabsList>
                 
                 <TabsContent value="flashcards" className="mt-4 text-sm text-muted-foreground">
                    Great for memorizing definitions, key terms, and concepts. The AI will generate front/back cards from your source material.
                 </TabsContent>
                 <TabsContent value="quiz" className="mt-4 text-sm text-muted-foreground">
                    Test your understanding with multiple choice questions. Includes explanations and citations for every answer.
                 </TabsContent>
               </Tabs>
             </CardContent>
           </Card>

           <Button 
             size="lg" 
             className="w-full text-lg h-12" 
             disabled={!scope || !user}
             onClick={handleStartSession}
           >
             <Sparkles className="mr-2 h-5 w-5" />
             Generate & Start Session
           </Button>
        </div>

        {/* Right Column: Info/Stats */}
        <div className="space-y-6">
          <Card className="bg-muted/50 border-dashed">
            <CardHeader>
              <CardTitle className="text-base">Why use SmartStudy?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
                <div className="flex gap-3">
                    <div className="bg-primary/20 p-2 rounded-md h-fit">
                        <BookCopy className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                        <p className="font-medium">Context-Aware</p>
                        <p className="text-muted-foreground">Questions are generated directly from your uploaded PDF documents.</p>
                    </div>
                </div>
                <div className="flex gap-3">
                    <div className="bg-primary/20 p-2 rounded-md h-fit">
                        <Sparkles className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                        <p className="font-medium">Instant Feedback</p>
                        <p className="text-muted-foreground">Get explanations for every answer to reinforce learning.</p>
                    </div>
                </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Recent Generated Content</CardTitle>
              <CardDescription>Latest flashcards/quizzes for the selected scope.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {historyLoading ? (
                <p className="text-muted-foreground">Loading history...</p>
              ) : history.length === 0 ? (
                <p className="text-muted-foreground">No generated history yet.</p>
              ) : (
                history.slice(0, 5).map((item) => (
                  <div key={item.id} className="rounded-md border p-3 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium capitalize">{item.type}</span>
                      <span className="text-xs text-muted-foreground">{item.scope}</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {item.created_at ? new Date(item.created_at).toLocaleString() : 'Stored'}
                    </p>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
