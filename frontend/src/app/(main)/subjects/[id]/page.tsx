"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { useSubjectStore } from "@/lib/store/subjectStore";
import { useDocumentStore } from "@/lib/store/documentStore";
import { Breadcrumb } from "@/components/common/Breadcrumb";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Settings, Sparkles } from "lucide-react";
import { DocumentList } from "@/components/documents/DocumentList";
import { DocumentUploadModal } from "@/components/documents/DocumentUploadModal";
import { ConfirmDialog } from "@/components/shared/ConfirmDialog";
import { toast } from "sonner";
import { SubjectModal } from "@/components/subjects/SubjectModal";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/lib/store/authStore";
import { generateFlashcards, generateQuiz, getGeneratedHistory } from "@/lib/api/study";
import { Flashcard, QuizQuestion } from "@/types/models";
import { GeneratedHistoryItem } from "@/types/api";

type StudyMode = "flashcards" | "quiz";

export default function SubjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const user = useAuthStore((state) => state.user);
  
  const { subjects, selectedSubject, fetchSubjectById } = useSubjectStore();
  const { documents, isLoading, fetchDocuments, deleteDocument } = useDocumentStore();

  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isEditSubjectOpen, setIsEditSubjectOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState<string | null>(null);
  const [mode, setMode] = useState<StudyMode>("flashcards");
  const [query, setQuery] = useState("");
  const [count, setCount] = useState(6);
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">("medium");
  const [isGenerating, setIsGenerating] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [history, setHistory] = useState<GeneratedHistoryItem[]>([]);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string | null>(null);
  const [generatedFlashcards, setGeneratedFlashcards] = useState<Flashcard[]>([]);
  const [generatedQuiz, setGeneratedQuiz] = useState<QuizQuestion[]>([]);

  // Find subject from store or fetch
  const subject = subjects.find((s) => s.id === id) ?? (selectedSubject?.id === id ? selectedSubject : null);

  useEffect(() => {
    // Ideally fetchSubjectById would populate the specific subject if not found
    // For now we assume subjects are loaded or we fetch them
    if (!subject) {
       // In a real app we would fetch the single subject here
       fetchSubjectById(id);
    }
    fetchDocuments(id);
  }, [id, subject, fetchSubjectById, fetchDocuments]);

  useEffect(() => {
    const loadHistory = async () => {
      if (!user) {
        setHistory([]);
        return;
      }
      try {
        setHistoryLoading(true);
        const response = await getGeneratedHistory({
          user_id: user.id,
          scope: "subject",
          scope_id: id,
          limit: 8,
        });
        setHistory(response.items ?? []);
      } catch {
        setHistory([]);
      } finally {
        setHistoryLoading(false);
      }
    };

    void loadHistory();
  }, [id, user]);

  useEffect(() => {
    if (history.length === 0) {
      setSelectedHistoryId(null);
      return;
    }
    if (!selectedHistoryId || !history.some((item) => item.id === selectedHistoryId)) {
      setSelectedHistoryId(history[0].id);
    }
  }, [history, selectedHistoryId]);

  const handleDeleteDocument = (docId: string) => {
    setDocToDelete(docId);
  };

  const handleConfirmDelete = async () => {
    if (docToDelete) {
      await deleteDocument(docToDelete);
      setDocToDelete(null);
      toast.success("Document deleted");
    }
  };

  const handleEditSubject = async (data: any) => {
    // Placeholder for update logic
    toast.info("Subject updated (mock)");
    setIsEditSubjectOpen(false);
  };

  // Filter documents
  const pdfs = documents.filter(d => d.document_type === 'pdf');
  const summaries = documents.filter(d => d.document_type === 'summary');

  const handleGenerate = async () => {
    if (!user) {
      toast.error("Please login to generate content");
      return;
    }

    try {
      setIsGenerating(true);
      const cleanQuery = query.trim();

      if (mode === "flashcards") {
        const result = await generateFlashcards({
          scope: "subject",
          scope_id: id,
          ...(cleanQuery ? { query: cleanQuery } : {}),
          user_id: user.id,
          count,
          prompt_profile: "concise",
          save: true,
        });
        setGeneratedFlashcards(result.flashcards);
        setGeneratedQuiz([]);
      } else {
        const result = await generateQuiz({
          scope: "subject",
          scope_id: id,
          ...(cleanQuery ? { query: cleanQuery } : {}),
          user_id: user.id,
          count,
          difficulty,
          prompt_profile: "exam",
          save: true,
        });
        setGeneratedQuiz(result.questions);
        setGeneratedFlashcards([]);
      }

      const historyResponse = await getGeneratedHistory({
        user_id: user.id,
        scope: "subject",
        scope_id: id,
        limit: 8,
      });
      setHistory(historyResponse.items ?? []);
      toast.success("Content generated");
    } catch (error: any) {
      toast.error(error?.message || "Failed to generate content");
    } finally {
      setIsGenerating(false);
    }
  };

  const selectedHistoryItem = history.find((item) => item.id === selectedHistoryId) ?? null;
  const selectedPayload = (selectedHistoryItem?.content_json ?? {}) as {
    flashcards?: Array<{ front?: string; back?: string }>;
    questions?: Array<{
      question?: string;
      options?: string[];
      correct_answer?: number;
      explanation?: string;
    }>;
  };

  if (!subject) {
    return <div>Loading subject...</div>; // Or better skeleton
  }

  return (
    <div className="space-y-4">
      <Breadcrumb 
        items={[
          { label: "Subjects", href: "/subjects" },
          { label: subject.name }
        ]} 
      />

      {/* Header */}
      <div 
        className="rounded-xl p-5 text-white relative overflow-hidden shadow-md"
        style={{ backgroundColor: subject.color || '#3B82F6' }}
      >
        <div className="relative z-10 flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold mb-1">{subject.name}</h1>
            <p className="opacity-90 max-w-2xl text-sm">{subject.description}</p>
          </div>
          <Button 
            variant="secondary" 
            size="sm" 
            className="bg-white/20 hover:bg-white/30 text-white border-none"
            onClick={() => setIsEditSubjectOpen(true)}
          >
            <Settings className="h-4 w-4 mr-2" />
            Edit Subject
          </Button>
        </div>
        
        {/* Decorative background circle */}
        <div className="absolute -right-10 -bottom-20 w-52 h-52 bg-white/10 rounded-full blur-3xl" />
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle>Generate Study Content Here</CardTitle>
            <CardDescription>
              Generate flashcards or quizzes directly in this subject without leaving the page.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Tabs value={mode} onValueChange={(value) => setMode(value as StudyMode)}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="flashcards">Flashcards</TabsTrigger>
                <TabsTrigger value="quiz">Quiz</TabsTrigger>
              </TabsList>
            </Tabs>

            <div className="grid gap-2.5 md:grid-cols-3">
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="subject-generate-query">Topic (optional)</Label>
                <Input
                  id="subject-generate-query"
                  placeholder="Leave empty to let system choose best concepts"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  className="h-9"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="subject-generate-count">Count</Label>
                <Input
                  id="subject-generate-count"
                  type="number"
                  min={1}
                  max={20}
                  value={count}
                  onChange={(event) => setCount(Math.max(1, Math.min(20, Number(event.target.value) || 1)))}
                  className="h-9"
                />
              </div>
            </div>

            {mode === "quiz" && (
              <div className="space-y-2">
                <Label>Difficulty</Label>
                <Tabs value={difficulty} onValueChange={(value) => setDifficulty(value as "easy" | "medium" | "hard")}>
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="easy">Easy</TabsTrigger>
                    <TabsTrigger value="medium">Medium</TabsTrigger>
                    <TabsTrigger value="hard">Hard</TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>
            )}

            <Button onClick={handleGenerate} disabled={!user || isGenerating} className="w-full md:w-auto h-9">
              <Sparkles className="h-4 w-4 mr-2" />
              {isGenerating ? "Generating..." : "Generate in this page"}
            </Button>

            <div className="flex flex-wrap gap-2">
              <Button asChild variant="outline" size="sm">
                <Link href={`/subjects/${id}/flashcards`}>Open Flashcards Page</Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link href={`/subjects/${id}/quiz`}>Open Quiz Page</Link>
              </Button>
            </div>

            {generatedFlashcards.length > 0 && (
              <div className="space-y-1.5">
                <h3 className="font-medium">Latest Flashcards</h3>
                {generatedFlashcards.slice(0, 3).map((card) => (
                  <div key={card.id} className="rounded-md border p-2.5">
                    <p className="font-medium text-sm">{card.front}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{card.back}</p>
                  </div>
                ))}
              </div>
            )}

            {generatedQuiz.length > 0 && (
              <div className="space-y-1.5">
                <h3 className="font-medium">Latest Quiz</h3>
                {generatedQuiz.slice(0, 2).map((question) => (
                  <div key={question.id} className="rounded-md border p-2.5 space-y-1.5">
                    <p className="font-medium text-sm">{question.question}</p>
                    <ul className="text-xs text-muted-foreground list-disc pl-4 space-y-0.5">
                      {question.options.map((option, index) => (
                        <li key={`${question.id}-${index}`}>{option}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle>Previous Generated Content</CardTitle>
            <CardDescription>Click an item to inspect its full generated content.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {historyLoading ? (
              <p className="text-sm text-muted-foreground">Loading history...</p>
            ) : history.length === 0 ? (
              <p className="text-sm text-muted-foreground">No generated content yet for this subject.</p>
            ) : (
              <div className="space-y-1.5 max-h-[320px] overflow-auto pr-1">
                {history.slice(0, 8).map((item) => {
                  const payload = item.content_json as {
                    flashcards?: unknown[];
                    questions?: unknown[];
                  };
                  const countLabel = item.type === "flashcard"
                    ? `${payload.flashcards?.length ?? 0} cards`
                    : `${payload.questions?.length ?? 0} questions`;
                  const isSelected = selectedHistoryId === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setSelectedHistoryId(item.id)}
                      className={`w-full rounded-md border p-2.5 text-left transition-colors ${
                        isSelected ? "border-primary bg-primary/5" : "hover:bg-muted/40"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-medium capitalize text-sm">{item.type}</p>
                          <p className="text-xs text-muted-foreground">
                            {item.created_at ? new Date(item.created_at).toLocaleString() : "Stored"}
                          </p>
                        </div>
                        <p className="text-xs text-muted-foreground">{countLabel}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {selectedHistoryItem && (
              <div className="rounded-md border p-2.5 space-y-2">
                <p className="text-sm font-medium">
                  Selected: <span className="capitalize">{selectedHistoryItem.type}</span>
                </p>

                <Button asChild size="sm" variant="outline">
                  <Link
                    href={`/subjects/${id}/study?history=${selectedHistoryItem.id}`}
                  >
                    Open Study Session
                  </Link>
                </Button>

                {selectedHistoryItem.type === "flashcard" ? (
                  (selectedPayload.flashcards ?? []).length === 0 ? (
                    <p className="text-sm text-muted-foreground">No flashcards in this entry.</p>
                  ) : (
                    <div className="space-y-1.5 max-h-[300px] overflow-auto pr-1">
                      {(selectedPayload.flashcards ?? []).slice(0, 8).map((card, index) => (
                        <div key={`${selectedHistoryItem.id}-card-${index}`} className="rounded-md border p-2">
                          <p className="text-sm font-medium">{card.front || `Card ${index + 1}`}</p>
                          <p className="text-xs text-muted-foreground mt-1">{card.back || ""}</p>
                        </div>
                      ))}
                    </div>
                  )
                ) : (selectedPayload.questions ?? []).length === 0 ? (
                  <p className="text-sm text-muted-foreground">No quiz questions in this entry.</p>
                ) : (
                  <div className="space-y-1.5 max-h-[300px] overflow-auto pr-1">
                    {(selectedPayload.questions ?? []).slice(0, 6).map((question, index) => (
                      <div key={`${selectedHistoryItem.id}-q-${index}`} className="rounded-md border p-2 space-y-1">
                        <p className="text-sm font-medium">{question.question || `Question ${index + 1}`}</p>
                        <ul className="text-xs text-muted-foreground list-disc pl-4 space-y-0.5">
                          {(question.options ?? []).map((option, optionIndex) => (
                            <li key={`${selectedHistoryItem.id}-q-${index}-opt-${optionIndex}`}>{option}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

        <Tabs defaultValue="all" className="w-full">
         <div className="flex justify-between items-center mb-6">
            <TabsList>
              <TabsTrigger value="all">All Documents ({documents.length})</TabsTrigger>
              <TabsTrigger value="pdfs">PDFs ({pdfs.length})</TabsTrigger>
              <TabsTrigger value="summaries">Summaries ({summaries.length})</TabsTrigger>
            </TabsList>

            <div className="flex gap-2">
              <Button onClick={() => setIsUploadOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Document
              </Button>
            </div>
         </div>

         <TabsContent value="all" className="mt-0">
           <DocumentList 
             documents={documents} 
             isLoading={isLoading}
             onView={(docId) => console.log("View", docId)}
             onDelete={handleDeleteDocument}
           />
         </TabsContent>
         
         <TabsContent value="pdfs" className="mt-0">
            <DocumentList 
             documents={pdfs} 
             isLoading={isLoading}
             onView={(docId) => console.log("View", docId)}
             onDelete={handleDeleteDocument}
           />
         </TabsContent>

         <TabsContent value="summaries" className="mt-0">
            <DocumentList 
             documents={summaries} 
             isLoading={isLoading}
             onView={(docId) => console.log("View", docId)}
             onDelete={handleDeleteDocument}
           />
         </TabsContent>
       </Tabs>

      <DocumentUploadModal
        open={isUploadOpen}
        onOpenChange={setIsUploadOpen}
        subjectId={id}
      />

      <SubjectModal
        open={isEditSubjectOpen}
        onOpenChange={setIsEditSubjectOpen}
        onSubmit={handleEditSubject}
        initialData={subject}
        isLoading={false}
      />

      <ConfirmDialog
        open={!!docToDelete}
        onOpenChange={(open) => !open && setDocToDelete(null)}
        title="Delete Document"
        description="Are you sure you want to delete this document? This cannot be undone."
        onConfirm={handleConfirmDelete}
        confirmJson="Delete"
        variant="destructive"
      />
    </div>
  );
}
