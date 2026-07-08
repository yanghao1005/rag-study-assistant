"use client";

import { useEffect, useMemo, useState, use } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { Breadcrumb } from "@/components/common/Breadcrumb";
import { Button } from "@/components/ui/button";
import { FlashcardCarousel } from "@/components/study/FlashcardCarousel";
import { QuizInterface } from "@/components/study/QuizInterface";
import { HistorySidebar } from "@/components/study/HistorySidebar";
import { useAuthStore } from "@/lib/store/authStore";
import { getGeneratedHistory } from "@/lib/api/study";
import { Flashcard, QuizQuestion } from "@/types/models";
import { GeneratedHistoryItem } from "@/types/api";
import { ArrowLeft, Clock, History, Loader2, PlusCircle, BookOpen, HelpCircle } from "lucide-react";

export default function SubjectStudyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const searchParams = useSearchParams();
  const historyParam = searchParams.get("history");

  const [historyItems, setHistoryItems] = useState<GeneratedHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(historyParam);

  // Load history on mount
  useEffect(() => {
    async function loadHistory() {
      if (!user) return;
      try {
        setLoadingHistory(true);
        // Fetch ALL generated history for this subject (flashcards AND quizzes)
        const response = await getGeneratedHistory({
            user_id: user.id,
            scope: "subject",
            scope_id: id,
            limit: 50,
        });
        
        // No filter here - take everything
        const items = response.items || [];
        setHistoryItems(items);
        
        // Select first item if none selected and history param is missing
        if (items.length > 0 && !selectedHistoryId && !historyParam) {
            setSelectedHistoryId(items[0].id);
        } else if (historyParam && items.some(i => i.id === historyParam)) {
            setSelectedHistoryId(historyParam);
        }
      } catch (error) {
        console.error("Failed to load study history:", error);
      } finally {
        setLoadingHistory(false);
      }
    }
    
    loadHistory();
  }, [id, user]);

  // Handle selection change
  const handleSelectHistory = (historyId: string) => {
    setSelectedHistoryId(historyId);
    // Update URL shallowly
    const url = new URL(window.location.href);
    url.searchParams.set("history", historyId);
    window.history.pushState({}, "", url.toString());
  };

  // Memoize the selected content data
  const selectedContent = useMemo<{ type: 'flashcard' | 'quiz', data: any[] } | null>(() => {
    if (!selectedHistoryId) return null;
    
    const selectedItem = historyItems.find(item => item.id === selectedHistoryId);
    if (!selectedItem) return null;

    try {
        const content = selectedItem.content_json as any;
        
        if (selectedItem.type === 'flashcard') {
            const flashcards = content.flashcards || [];
            if (!Array.isArray(flashcards)) return null;
            
            return {
                type: 'flashcard',
                data: flashcards.map((card: any, index: number) => ({
                    id: card.id || `${selectedItem.id}-${index}`,
                    front: card.front,
                    back: card.back,
                    source: card.source
                }))
            };
        } else if (selectedItem.type === 'quiz') {
            const questions = content.questions || [];
            if (!Array.isArray(questions)) return null;
            
            return {
                type: 'quiz',
                data: questions.map((q: any, index: number) => ({
                    id: q.id || `${selectedItem.id}-${index}`,
                    question: q.question,
                    options: q.options || [],
                    correct_answer: q.correct_answer,
                    explanation: q.explanation,
                    source: q.source
                }))
            };
        }
        
        return null;
    } catch (e) {
        console.error("Error parsing content:", e);
        return null;
    }
  }, [selectedHistoryId, historyItems]);

  const displayTitle = useMemo(() => {
      if (!selectedHistoryId) return "Study Session";
      const index = historyItems.findIndex(item => item.id === selectedHistoryId);
      const item = historyItems[index];
      if (!item) return "Study Session";
      
      const setNumber = historyItems.length - index;
      const typeLabel = item.type === 'flashcard' ? 'Flashcard Set' : 'Quiz';
      
      // Try to get document name from first item's source if available
      let sourceName = "";
      try {
          const content = item.content_json as any;
          if (item.type === 'flashcard' && content.flashcards?.[0]?.source?.document) {
              sourceName = content.flashcards[0].source.document;
          } else if (item.type === 'quiz' && content.questions?.[0]?.source?.document) {
              sourceName = content.questions[0].source.document;
          }
      } catch (e) {}

      if (sourceName) {
          return `${typeLabel} from ${sourceName}`;
      }
      return `${typeLabel} #${setNumber}`;
  }, [selectedHistoryId, historyItems]);

  return (
    <div className="container mx-auto py-6 space-y-6 max-w-7xl">
      <Breadcrumb
        items={[
          { label: "Subjects", href: "/dashboard" },
          { label: "Subject", href: `/subjects/${id}` },
          { label: "Study" },
        ]}
      />

      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/subjects/${id}`}>
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Study Center</h1>
          <p className="text-muted-foreground">
            Review all your generated study materials for this subject
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Sidebar - History List */}
        <div className="lg:col-span-3 order-2 lg:order-1">
            <HistorySidebar 
                items={historyItems}
                selectedId={selectedHistoryId} 
                onSelect={handleSelectHistory}
                title="Study History"
                description="Select a session to review"
                loading={loadingHistory}
                className="h-[calc(100vh-200px)] sticky top-6"
            />
        </div>

        {/* Main Content - Interface */}
        <div className="lg:col-span-9 xl:col-span-9 order-1 lg:order-2 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    {selectedContent?.type === 'flashcard' ? (
                        <BookOpen className="h-5 w-5 text-primary" />
                    ) : (
                        <HelpCircle className="h-5 w-5 text-primary" />
                    )}
                    {displayTitle}
                </h2>
                {selectedContent && (
                    <span className="text-sm text-muted-foreground bg-secondary px-2 py-1 rounded-md">
                        {selectedContent.data.length} items
                    </span>
                )}
            </div>

            {loadingHistory ? (
                <div className="flex items-center justify-center h-96 border rounded-xl bg-muted/5">
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        <p className="text-muted-foreground animate-pulse">Loading study material...</p>
                    </div>
                </div>
            ) : selectedContent ? (
                <div className="bg-background rounded-xl min-h-125">
                    {selectedContent.type === 'flashcard' ? (
                        <FlashcardCarousel flashcards={selectedContent.data as Flashcard[]} />
                    ) : (
                        <QuizInterface 
                            key={selectedHistoryId} 
                            persistenceKey={selectedHistoryId ? `quiz-progress-${selectedHistoryId}` : undefined}
                            questions={selectedContent.data as QuizQuestion[]} 
                            onRetake={() => {
                                // Handled internally
                            }}
                        />
                    )}
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center h-96 border-2 border-dashed rounded-xl p-8 text-center space-y-6 bg-muted/5">
                    <div className="bg-primary/10 p-6 rounded-full ring-8 ring-primary/5">
                        <PlusCircle className="h-10 w-10 text-primary" />
                    </div>
                    <div className="max-w-md space-y-2">
                        <h3 className="text-xl font-bold">No Content Selected</h3>
                        <p className="text-muted-foreground">
                            {historyItems.length === 0 
                                ? "You haven't generated any study material yet."
                                : "Select an item from the sidebar to continue studying."}
                        </p>
                    </div>
                    {historyItems.length === 0 && (
                        <Button asChild size="lg" className="mt-4">
                            <Link href={`/subjects/${id}?action=generate`}>
                                Generate Content
                            </Link>
                        </Button>
                    )}
                </div>
            )}
        </div>
      </div>
    </div>
  );
}
