"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { SubjectRequired } from "@/components/auth/subject-required";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useSubjectDocuments } from "@/features/documents/use-subject-documents";
import { useSessionStore } from "@/features/auth/session-store";
import { useGenerateFlashcards, useGenerateQuiz } from "@/features/generation/use-generation";

export default function GeneratePage() {
  const router = useRouter();
  const { token, subjectId } = useSessionStore();
  const subjectDocumentsQuery = useSubjectDocuments({
    token,
    subjectId,
    enabled: Boolean(token && subjectId),
  });

  const subjectDocuments = subjectDocumentsQuery.data?.items ?? [];
  const hasSubjectContext = Boolean((subjectId || "").trim());
  const hasDocumentsInSubject = subjectDocuments.length > 0;
  const allDocumentIds = subjectDocuments.map((item) => item.id);

  const [query, setQuery] = useState("main concepts and methods");
  const [flashcardCount, setFlashcardCount] = useState(5);
  const [quizCount, setQuizCount] = useState(5);
  const [scopeMode, setScopeMode] = useState<"all" | "selected">("all");
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);

  const flashcardsMutation = useGenerateFlashcards();
  const quizMutation = useGenerateQuiz();
  const canGenerate = hasSubjectContext && hasDocumentsInSubject && (scopeMode === "all" || selectedDocumentIds.length > 0);

  const toggleDocument = (documentId: string) => {
    setSelectedDocumentIds((previous) =>
      previous.includes(documentId) ? previous.filter((id) => id !== documentId) : [...previous, documentId],
    );
  };

  const sourceDocumentIds =
    scopeMode === "selected" ? selectedDocumentIds.filter((id) => allDocumentIds.includes(id)) : [];

  const runFlashcards = async () => {
    if (!token) {
      toast.error("Token is required.");
      return;
    }
    if (!hasSubjectContext) {
      toast.error("Select a subject first.");
      return;
    }
    if (!hasDocumentsInSubject) {
      toast.error("No documents found for this subject. Upload one first.");
      return;
    }
    if (!canGenerate) {
      toast.error("Select at least one document in selected scope mode.");
      return;
    }
    try {
      const response = await flashcardsMutation.mutateAsync({
        token,
        scope: "subject",
        scopeId: subjectId,
        sourceDocumentIds,
        query,
        count: flashcardCount,
      });
      toast.success("Flashcards generated.");
      if (response.generated_id) {
        router.push(`/flashcards?group=${response.generated_id}`);
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Generation failed.");
    }
  };

  const runQuiz = async () => {
    if (!token) {
      toast.error("Token is required.");
      return;
    }
    if (!hasSubjectContext) {
      toast.error("Select a subject first.");
      return;
    }
    if (!hasDocumentsInSubject) {
      toast.error("No documents found for this subject. Upload one first.");
      return;
    }
    if (!canGenerate) {
      toast.error("Select at least one document in selected scope mode.");
      return;
    }
    try {
      const response = await quizMutation.mutateAsync({
        token,
        scope: "subject",
        scopeId: subjectId,
        sourceDocumentIds,
        query,
        count: quizCount,
        difficulty: "medium",
      });
      toast.success("Quiz generated.");
      if (response.generated_id) {
        router.push(`/quizzes?group=${response.generated_id}`);
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Generation failed.");
    }
  };

  return (
    <SubjectRequired>
      <div className="mx-auto grid w-full max-w-6xl gap-6 lg:grid-cols-2">
      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <CardTitle>Generation Controls</CardTitle>
          <CardDescription>Generate from all subject documents or choose an exact multi-document scope.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="rounded-md bg-muted p-3 text-xs text-muted-foreground">
            {hasDocumentsInSubject
              ? `Searching across ${subjectDocuments.length} uploaded document${subjectDocuments.length === 1 ? "" : "s"} in this subject.`
              : subjectDocumentsQuery.isLoading
                ? "Resolving subject documents..."
                : "No uploaded documents found in this subject yet."}
          </div>

          <div className="grid gap-2">
            <Label>Scope</Label>
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant={scopeMode === "all" ? "default" : "outline"}
                onClick={() => setScopeMode("all")}
                className="rounded-sl-standard"
              >
                All documents
              </Button>
              <Button
                type="button"
                variant={scopeMode === "selected" ? "default" : "outline"}
                onClick={() => setScopeMode("selected")}
                className="rounded-sl-standard"
              >
                Selected documents
              </Button>
            </div>
          </div>

          {scopeMode === "selected" ? (
            <div className="grid gap-2">
              <div className="flex items-center justify-between">
                <Label>Select documents</Label>
                <Button
                  type="button"
                  variant="ghost"
                  className="h-auto px-2 py-1 text-xs"
                  onClick={() => setSelectedDocumentIds(allDocumentIds)}
                >
                  Select all
                </Button>
              </div>
              <div className="max-h-40 space-y-1 overflow-auto rounded-md border border-[var(--sl-muted)] p-2">
                {subjectDocuments.map((document) => {
                  const checked = selectedDocumentIds.includes(document.id);
                  return (
                    <button
                      key={document.id}
                      type="button"
                      onClick={() => toggleDocument(document.id)}
                      className={`flex w-full items-center justify-between rounded-md px-2 py-1 text-left text-sm transition ${checked ? "bg-[rgba(167,139,250,0.12)] text-[var(--sl-lavender)]" : "hover:bg-muted"}`}
                    >
                      <span className="truncate">{document.filename}</span>
                      <span className="ml-2 text-xs">{checked ? "selected" : ""}</span>
                    </button>
                  );
                })}
              </div>
              <p className="text-xs text-muted-foreground">{selectedDocumentIds.length} selected</p>
            </div>
          ) : null}

          <div className="grid gap-2">
            <Label htmlFor="query">Query focus</Label>
            <Textarea id="query" value={query} onChange={(event) => setQuery(event.target.value)} />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="flashcard-count">Flashcard count</Label>
            <Input
              id="flashcard-count"
              type="number"
              min={1}
              max={25}
              value={flashcardCount}
              onChange={(event) => setFlashcardCount(Number(event.target.value || 5))}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="quiz-count">Quiz count</Label>
            <Input
              id="quiz-count"
              type="number"
              min={1}
              max={20}
              value={quizCount}
              onChange={(event) => setQuizCount(Number(event.target.value || 5))}
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <Button
              onClick={runFlashcards}
              disabled={flashcardsMutation.isPending || subjectDocumentsQuery.isLoading || !canGenerate}
              className="rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]"
            >
              {flashcardsMutation.isPending ? "Generating..." : "Generate Flashcards"}
            </Button>
            <Button
              onClick={runQuiz}
              disabled={quizMutation.isPending || subjectDocumentsQuery.isLoading || !canGenerate}
              variant="secondary"
              className="rounded-sl-standard"
            >
              {quizMutation.isPending ? "Generating..." : "Generate Quiz"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <CardTitle>Live Output</CardTitle>
          <CardDescription>Backend response preview for fast iteration and prompt tuning.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 text-sm">
          <div className="grid gap-1">
            <p className="font-medium">Flashcards</p>
            <pre className="max-h-56 overflow-auto rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(flashcardsMutation.data?.flashcards || [], null, 2)}
            </pre>
          </div>
          <div className="grid gap-1">
            <p className="font-medium">Quiz</p>
            <pre className="max-h-56 overflow-auto rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(quizMutation.data?.questions || [], null, 2)}
            </pre>
          </div>
        </CardContent>
      </Card>
      </div>
    </SubjectRequired>
  );
}

