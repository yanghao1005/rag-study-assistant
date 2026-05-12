"use client";

import { SubjectRequired } from "@/components/auth/subject-required";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useSessionStore } from "@/features/auth/session-store";
import { useGenerationHistory } from "@/features/history/use-history";

export default function HistoryPage() {
  const { token, documentId } = useSessionStore();
  const historyQuery = useGenerationHistory({
    token,
    scope: "document",
    scopeId: documentId,
    enabled: Boolean(token && documentId),
    limit: 20,
  });

  return (
    <SubjectRequired>
      <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Generated History</CardTitle>
          <CardDescription>Latest flashcards, quiz outputs, summaries, and chat answers for this document scope.</CardDescription>
        </CardHeader>
        <CardContent>
          <pre className="max-h-[70vh] overflow-auto rounded-md bg-muted p-3 text-xs">
            {JSON.stringify(historyQuery.data?.items || [], null, 2)}
          </pre>
        </CardContent>
      </Card>
      </div>
    </SubjectRequired>
  );
}
