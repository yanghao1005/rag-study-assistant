"use client";

import Link from "next/link";
import { useEffect } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useSessionStore } from "@/features/auth/session-store";

export default function DocumentWorkspacePage({ params }: { params: { documentId: string } }) {
  const { setDocumentId } = useSessionStore();

  useEffect(() => {
    setDocumentId(params.documentId);
  }, [params.documentId, setDocumentId]);

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <Badge className="w-fit">Active Document</Badge>
          <CardTitle className="font-mono text-base">{params.documentId}</CardTitle>
          <CardDescription>
            Document context is now bound for generation, chat, and history pages through shared session state.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button asChild>
            <Link href="/generate">Generate Flashcards/Quiz</Link>
          </Button>
          <Button asChild variant="secondary">
            <Link href="/chat">Ask Chat</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/history">Open History</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
