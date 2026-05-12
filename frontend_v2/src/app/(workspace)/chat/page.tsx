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
  const [question, setQuestion] = useState("What is this document mainly about?");
  const chatMutation = useAskChat();

  const runAsk = async () => {
    if (!token || !documentId) {
      toast.error("Token and document ID are required.");
      return;
    }
    try {
      await chatMutation.mutateAsync({
        token,
        scope: "document",
        scopeId: documentId,
        question,
      });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Chat failed.");
    }
  };

  return (
    <SubjectRequired>
      <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>Grounded Chat</CardTitle>
          <CardDescription>Ask document-scoped questions and inspect confidence/citations.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="question">Question</Label>
            <Textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} />
          </div>
          <Button onClick={runAsk} disabled={chatMutation.isPending}>
            {chatMutation.isPending ? "Asking..." : "Ask"}
          </Button>
        </CardContent>
      </Card>

      <Card>
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
