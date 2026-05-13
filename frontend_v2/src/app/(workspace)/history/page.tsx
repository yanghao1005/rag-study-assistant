"use client";

import Link from "next/link";

import { SubjectRequired } from "@/components/auth/subject-required";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useSessionStore } from "@/features/auth/session-store";
import { useGenerationHistory } from "@/features/history/use-history";
import { ApiError } from "@/lib/api/http";

export default function HistoryPage() {
  const { token, subjectId } = useSessionStore();
  const normalizedSubjectId = (subjectId || "").trim();
  const hasSubjectContext = Boolean(normalizedSubjectId) && normalizedSubjectId.toLowerCase() !== "undefined" && normalizedSubjectId.toLowerCase() !== "null";

  const historyQuery = useGenerationHistory({
    token,
    scope: "subject",
    scopeId: normalizedSubjectId,
    enabled: Boolean(token && hasSubjectContext),
    limit: 100,
  });

  const networkError = historyQuery.error instanceof ApiError && historyQuery.error.status === 0;

  return (
    <SubjectRequired>
      <div className="mx-auto grid w-full max-w-6xl gap-6">
      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <CardTitle>Generated History</CardTitle>
          <CardDescription>All generated groups for this subject. Open any group in the dedicated editor pages.</CardDescription>
        </CardHeader>
        <CardContent>
            {!hasSubjectContext ? <p className="text-sm text-muted-foreground">Select a subject first to load history.</p> : null}
            {historyQuery.isLoading ? <p className="text-sm text-muted-foreground">Loading history...</p> : null}
            {historyQuery.isError ? (
              <p className="text-sm text-[var(--sl-rose)]">
                {networkError
                  ? "Could not connect to backend_v5. Make sure API is running and reachable at localhost:8000."
                  : historyQuery.error instanceof Error
                    ? historyQuery.error.message
                    : "Failed to load history."}
              </p>
            ) : null}

            {!historyQuery.isLoading && !historyQuery.isError ? (
              <div className="space-y-3">
                {(historyQuery.data?.items || []).map((item) => {
                  const meta = (item.content_json || {}) as Record<string, unknown>;
                  const query = (meta.meta as Record<string, unknown> | undefined)?.query;
                  const sourceDocumentIds = (meta.meta as Record<string, unknown> | undefined)?.source_document_ids;

                  return (
                    <div key={item.id} className="rounded-md border border-[var(--sl-muted)] p-3 text-sm">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div>
                          <p className="font-medium">{item.type.toUpperCase()} group</p>
                          <p className="text-xs text-muted-foreground">{item.created_at || "Unknown date"}</p>
                        </div>
                        <div className="flex gap-2">
                          {item.type === "flashcard" ? (
                            <>
                              <Button asChild size="sm" variant="secondary" className="rounded-sl-standard">
                                <Link href={`/flashcards?group=${item.id}`}>Open Flashcards</Link>
                              </Button>
                              <Button asChild size="sm" variant="outline" className="rounded-sl-standard">
                                <Link href={`/flashcards/edit?group=${item.id}`}>Edit Flashcards</Link>
                              </Button>
                            </>
                          ) : null}
                          {item.type === "quiz" ? (
                            <>
                              <Button asChild size="sm" variant="secondary" className="rounded-sl-standard">
                                <Link href={`/quizzes?group=${item.id}`}>Open Quiz</Link>
                              </Button>
                              <Button asChild size="sm" variant="outline" className="rounded-sl-standard">
                                <Link href={`/quizzes/edit?group=${item.id}`}>Edit Quiz</Link>
                              </Button>
                            </>
                          ) : null}
                        </div>
                      </div>

                      <div className="mt-2 text-xs text-muted-foreground">
                        <p>Query: {typeof query === "string" && query ? query : "n/a"}</p>
                        <p>
                          Sources: {Array.isArray(sourceDocumentIds) ? `${sourceDocumentIds.length} selected document(s)` : "all subject documents"}
                        </p>
                      </div>
                    </div>
                  );
                })}

                {!historyQuery.data?.items?.length ? <p className="text-sm text-muted-foreground">No generated groups for this subject yet.</p> : null}
              </div>
            ) : null}
        </CardContent>
      </Card>
      </div>
    </SubjectRequired>
  );
}
