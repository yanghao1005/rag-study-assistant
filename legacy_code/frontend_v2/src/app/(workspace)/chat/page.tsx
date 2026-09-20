"use client";

import { useState } from "react";
import { toast } from "sonner";

import { SubjectRequired } from "@/components/auth/subject-required";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useSessionStore } from "@/features/auth/session-store";
import { useAskChat } from "@/features/chat/use-chat";

export default function ChatPage() {
  const { token, documentId } = useSessionStore();
  const normalizedDocumentId = (documentId || "").trim();
  const hasDocumentContext = Boolean(normalizedDocumentId) && normalizedDocumentId.toLowerCase() !== "undefined" && normalizedDocumentId.toLowerCase() !== "null";
  const [question, setQuestion] = useState("What is this document mainly about?");
  const chatMutation = useAskChat();

  const runAsk = async () => {
    if (!token || !hasDocumentContext) {
      toast.error("Token and document ID are required.");
      return;
    }
    try {
      await chatMutation.mutateAsync({
        token,
        scope: "document",
        scopeId: normalizedDocumentId,
        question,
      });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Chat failed.");
    }
  };

  return (
    <SubjectRequired>
      <div className="mx-auto grid w-full max-w-6xl gap-6 lg:grid-cols-[1.1fr_1fr]">
      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <CardTitle>Grounded Chat</CardTitle>
          <CardDescription>Ask document-scoped questions and inspect confidence/citations.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="question">Question</Label>
            <Textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} />
          </div>
          <Button onClick={runAsk} disabled={chatMutation.isPending} className="rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]">
            {chatMutation.isPending ? "Asking..." : "Ask"}
          </Button>
        </CardContent>
      </Card>

      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <CardTitle>Response</CardTitle>
          <CardDescription>Answer, confidence, and citations from backend_v5.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm">
          <p>
            <span className="text-muted-foreground">Confidence:</span> {chatMutation.data?.confidence ?? "-"}
          </p>
          <pre className="max-h-72 overflow-auto rounded-md bg-muted p-3 text-xs">{chatMutation.data?.answer || "No answer yet."}</pre>
          <pre className="max-h-72 overflow-auto rounded-md bg-muted p-3 text-xs">
            {JSON.stringify(chatMutation.data?.citations || [], null, 2)}
          </pre>
        </CardContent>
      </Card>
      </div>
    </SubjectRequired>
  );
}

