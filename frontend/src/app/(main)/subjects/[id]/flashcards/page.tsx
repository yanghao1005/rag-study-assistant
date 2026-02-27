"use client";

import { useEffect, useMemo, useState, use } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { Breadcrumb } from "@/components/common/Breadcrumb";
import { Button } from "@/components/ui/button";
import { FlashcardCarousel } from "@/components/study/FlashcardCarousel";
import { HistorySidebar } from "@/components/study/HistorySidebar";
import { useAuthStore } from "@/lib/store/authStore";
import { getGeneratedHistory } from "@/lib/api/study";
import { Flashcard } from "@/types/models";
import { GeneratedHistoryItem } from "@/types/api";
import { ArrowLeft, Clock, History, Loader2, PlusCircle } from "lucide-react";

export default function SubjectFlashcardsPage({ params }: { params: Promise<{ id: string }> }) {
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
        const response = await getGeneratedHistory({
            user_id: user.id,
            scope: "subject",
            scope_id: id,
            limit: 50,
        });
        
        // Filter only flashcards
        const items = (response.items || []).filter(item => item.type === "flashcard");
        setHistoryItems(items);
        
        // Select first item if none selected and history param is missing
        if (items.length > 0 && !selectedHistoryId && !historyParam) {
            setSelectedHistoryId(items[0].id);
        } else if (historyParam && items.some(i => i.id === historyParam)) {
            setSelectedHistoryId(historyParam);
        }
      } catch (error) {
        console.error("Failed to load flashcard history:", error);
      } finally {
        setLoadingHistory(false);
      }
    }
    
    loadHistory();
  }, [id, user]); // Only run on mount + auth ready

  // Update selected ID when history items load if needed, but the main logic is inside loadHistory
  
  // Handle selection change
  const handleSelectHistory = (historyId: string) => {
    setSelectedHistoryId(historyId);
    // Update URL shallowly
    const url = new URL(window.location.href);
    url.searchParams.set("history", historyId);
    window.history.pushState({}, "", url.toString());
  };

  // Memoize the selected flashcards data
  const flashcards = useMemo<Flashcard[]>(() => {
    if (!selectedHistoryId) return [];
    
    const selectedItem = historyItems.find(item => item.id === selectedHistoryId);
    if (!selectedItem) return [];

    try {
        // Safe access to nested JSON structure
        const content = selectedItem.content_json;
        // Check if content has flashcards property (new format) or is array (old format maybe?)
        const cards = (content as any).flashcards || [];
        
        return cards.map((card: any, index: number) => ({
            id: card.id || `${selectedItem.id}-${index}`,
            front: card.front || "Empty front",
            back: card.back || "Empty back",
            source: card.source // Keep source reference if available
        }));
    } catch (e) {
        console.error("Error parsing flashcard content:", e);
        return [];
    }
  }, [selectedHistoryId, historyItems]);

  const selectedIndex = historyItems.findIndex(i => i.id === selectedHistoryId);
  const displayTitle = selectedIndex !== -1 ? `Flashcard Set ${historyItems.length - selectedIndex}` : "Flashcards";

  return (
    <div className="container max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header Section */}
      <div className="space-y-4">
        <Breadcrumb
            items={[
            { label: "Subjects", href: "/subjects" },
            { label: "Subject Details", href: `/subjects/${id}` },
            { label: "Flashcards", href: `/subjects/${id}/flashcards` },
            ]}
        />
        
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight">Flashcards</h1>
            <p className="text-muted-foreground text-lg">
              Master key concepts through spaced repetition.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" asChild size="sm">
                <Link href={`/subjects/${id}`}>
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to Subject
                </Link>
            </Button>
            <Button size="sm" asChild>
                <Link href={`/subjects/${id}?action=generate`}>
                    <PlusCircle className="mr-2 h-4 w-4" />
                    Generate New
                </Link>
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Sidebar - History List */}
        <div className="lg:col-span-3 xl:col-span-3 order-2 lg:order-1">
             <div className="sticky top-24 space-y-4">
                <HistorySidebar 
                    items={historyItems}
                    selectedId={selectedHistoryId}
                    onSelect={handleSelectHistory}
                    title="Saved Sets"
                    description={`Review your ${historyItems.length} saved sets`}
                    loading={loadingHistory}
                    className="h-[calc(100vh-12rem)] min-h-100"
                />
             </div>
        </div>

        {/* Main Content - Carousel */}
        <div className="lg:col-span-9 xl:col-span-9 order-1 lg:order-2 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                    <History className="h-5 w-5 text-muted-foreground" />
                    {displayTitle}
                </h2>
                <span className="text-sm text-muted-foreground bg-secondary px-2 py-1 rounded-md">
                    {flashcards.length} cards
                </span>
            </div>

            {loadingHistory ? (
                <div className="flex items-center justify-center h-96 border rounded-xl bg-muted/5">
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        <p className="text-muted-foreground animate-pulse">Loading cards...</p>
                    </div>
                </div>
            ) : flashcards.length > 0 ? (
                <div className="bg-background rounded-xl min-h-125 flex flex-col justify-center">
                    <FlashcardCarousel flashcards={flashcards} />
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center h-96 border-2 border-dashed rounded-xl p-8 text-center space-y-6 bg-muted/5">
                    <div className="bg-primary/10 p-6 rounded-full ring-8 ring-primary/5">
                        <PlusCircle className="h-10 w-10 text-primary" />
                    </div>
                    <div className="max-w-md space-y-2">
                        <h3 className="text-xl font-bold">No Flashcards Selected</h3>
                        <p className="text-muted-foreground">
                            {historyItems.length === 0 
                                ? "You haven't generated any flashcards yet. Start by generating new ones from your study materials."
                                : "Select a flashcard set from the sidebar to start reviewing."}
                        </p>
                    </div>
                    {historyItems.length === 0 && (
                        <Button asChild size="lg" className="mt-4">
                            <Link href={`/subjects/${id}?action=generate`}>
                                Generate Flashcards
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
