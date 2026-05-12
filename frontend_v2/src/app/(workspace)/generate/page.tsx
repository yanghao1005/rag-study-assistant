"use client";

import { useState } from "react";
import { toast } from "sonner";

import { SubjectRequired } from "@/components/auth/subject-required";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useSessionStore } from "@/features/auth/session-store";
import { useGenerateFlashcards, useGenerateQuiz } from "@/features/generation/use-generation";

export default function GeneratePage() {
  const { token, documentId } = useSessionStore();
  const [query, setQuery] = useState("main concepts and methods");
  const [flashcardCount, setFlashcardCount] = useState(5);
  const [quizCount, setQuizCount] = useState(5);

  const flashcardsMutation = useGenerateFlashcards();
  const quizMutation = useGenerateQuiz();

  const runFlashcards = async () => {
    if (!token || !documentId) {
      toast.error("Token and document ID are required.");
      return;
    }
    try {
      await flashcardsMutation.mutateAsync({
        token,
        scope: "document",
        scopeId: documentId,
        query,
        count: flashcardCount,
      });
      toast.success("Flashcards generated.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Generation failed.");
    }
  };

  const runQuiz = async () => {
    if (!token || !documentId) {
      toast.error("Token and document ID are required.");
      return;
    }
    try {
      await quizMutation.mutateAsync({
        token,
        scope: "document",
        scopeId: documentId,
        query,
        count: quizCount,
        difficulty: "medium",
      });
      toast.success("Quiz generated.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Generation failed.");
    }
  };

  return (
    <SubjectRequired>
      <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Generation Controls</CardTitle>
          <CardDescription>One query can drive both flashcards and quiz outputs for the active document.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
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
            <Button onClick={runFlashcards} disabled={flashcardsMutation.isPending}>
              {flashcardsMutation.isPending ? "Generating..." : "Generate Flashcards"}
            </Button>
            <Button onClick={runQuiz} disabled={quizMutation.isPending} variant="secondary">
              {quizMutation.isPending ? "Generating..." : "Generate Quiz"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
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
