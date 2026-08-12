"use client";

import { SubjectRequired } from "@/components/auth/subject-required";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useSessionStore } from "@/features/auth/session-store";
import { useGenerationHistory } from "@/features/history/use-history";

export default function FlashcardsLibraryPage() {
  const { token, subjectId, documentId } = useSessionStore();
  const scope = documentId ? "document" : "subject";
  const scopeId = documentId || subjectId;

  const history = useGenerationHistory({
    token,
    scope,
    scopeId,
    enabled: Boolean(token && scopeId),
    limit: 40,
  });

  const flashcardGroups = (history.data?.items || []).filter((item) => item.type === "flashcard");

  return (
    <SubjectRequired>
      <Card className="mx-auto w-full max-w-5xl border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <Badge className="w-fit">Flashcards</Badge>
          <CardTitle>Generated Flashcard Library</CardTitle>
          <CardDescription>Stored groups for the active scope.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3">
          {history.isLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : null}
          {flashcardGroups.length === 0 && !history.isLoading ? (
            <p className="text-sm text-muted-foreground">No flashcard groups saved yet.</p>
          ) : null}
          {flashcardGroups.map((group) => (
            <div key={group.id} className="rounded-md border border-[var(--sl-muted)] p-3">
              <p className="text-xs text-muted-foreground">Group ID</p>
              <p className="font-mono text-xs">{group.id}</p>
              <p className="mt-2 text-xs text-muted-foreground">Created</p>
              <p className="text-sm">{group.created_at || "-"}</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </SubjectRequired>
  );
}

