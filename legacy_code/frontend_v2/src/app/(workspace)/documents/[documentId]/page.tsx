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
    const normalized = (params.documentId || "").trim();
    if (!normalized || normalized.toLowerCase() === "undefined" || normalized.toLowerCase() === "null") {
      setDocumentId("");
      return;
    }
    setDocumentId(normalized);
  }, [params.documentId, setDocumentId]);

  return (
    <div className="mx-auto grid w-full max-w-6xl gap-6">
      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <Badge className="w-fit">Active Document</Badge>
          <CardTitle className="font-mono text-base">{params.documentId}</CardTitle>
          <CardDescription>
            Document context is now bound for generation, chat, and history pages through shared session state.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button asChild className="rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]">
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

