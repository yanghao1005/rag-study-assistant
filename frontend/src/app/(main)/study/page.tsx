"use client";

import { useState } from "react";
import { ScopeSelector, StudyScope } from "@/components/study/ScopeSelector";
import { FlashcardCarousel } from "@/components/study/FlashcardCarousel";
import { QuizInterface } from "@/components/study/QuizInterface";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BrainCircuit, BookCopy, Sparkles, ArrowLeft } from "lucide-react";
import { Flashcard, QuizQuestion } from "@/types/models";

// Mock Data Generators
const MOCK_FLASHCARDS: Flashcard[] = [
  {
    id: "1",
    front: "What is the primary function of the Mitochondria?",
    back: "The mitochondria is known as the powerhouse of the cell. It generates most of the chemical energy needed to power the cell's biochemical reactions.",
    source: { document: "Cell Biology 101", page: 45, document_type: "pdf" }
  },
  {
    id: "2",
    front: "Explain the process of Osmosis.",
    back: "Osmosis is the spontaneous net movement or diffusion of solvent molecules through a selectively permeable membrane from a region of high water potential to a region of low water potential, in the direction that tends to equalize the solute concentrations on the two sides.",
    source: { document: "Cell Biology 101", page: 12, document_type: "pdf" }
  },
  {
    id: "3",
    front: "What is Photosynthesis?",
    back: "Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight and turn it into chemical energy.",
    source: { document: "Plant Science", page: 88, document_type: "pdf" }
  }
];

const MOCK_QUIZ: QuizQuestion[] = [
  {
    id: "1",
    question: "Which organelle is responsible for protein synthesis?",
    options: ["Mitochondria", "Ribosome", "Golgi Apparatus", "Nucleus"],
    correct_answer: 1,
    explanation: "Ribosomes are the sites in a cell in which protein synthesis takes place.",
    source: { document: "Cell Biology 101", page: 32, document_type: "pdf" }
  },
  {
    id: "2",
    question: "What is the basic unit of life?",
    options: ["Atom", "Molecule", "Cell", "Organism"],
    correct_answer: 2,
    explanation: "The cell is the smallest structural and functional unit of an organism.",
    source: { document: "Biology Intro", page: 5, document_type: "pdf" }
  },
  {
    id: "3",
    question: "DNA is stored in which part of a eukaryote cell?",
    options: ["Cytoplasm", "Nucleus", "Cell Membrane", "Ribosome"],
    correct_answer: 1,
    explanation: "In eukaryotic cells, DNA is stored inside the nucleus.",
    source: { document: "Genetics Basics", page: 104, document_type: "pdf" }
  }
];

type StudyMode = 'flashcards' | 'quiz';

export default function StudyPage() {
  const [scope, setScope] = useState<StudyScope | null>(null);
  const [mode, setMode] = useState<StudyMode>('flashcards');
  const [sessionState, setSessionState] = useState<'config' | 'loading' | 'active'>('config');
  
  // Data State
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);

  const handleStartSession = async () => {
    if (!scope) return;
    
    setSessionState('loading');
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    if (mode === 'flashcards') {
        setFlashcards(MOCK_FLASHCARDS);
    } else {
        setQuizQuestions(MOCK_QUIZ);
    }
    
    setSessionState('active');
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
             Draft Mode • Mock Data
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
           <ScopeSelector onScopeChange={setScope} />
           
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
             disabled={!scope}
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
        </div>
      </div>
    </div>
  );
}
