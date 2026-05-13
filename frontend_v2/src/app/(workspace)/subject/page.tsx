"use client";

import Link from "next/link";
import { ArrowLeft, BookOpenText, FileUp, MessageCircle, Sparkles, Timer } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SubjectDocumentsManager } from "@/components/documents/subject-documents-manager";
import { useSessionStore } from "@/features/auth/session-store";
import { useSubjects } from "@/features/subjects/use-subjects";

export default function SubjectWorkspacePage() {
  const { token, subjectId, documentId } = useSessionStore();
  const subjectsQuery = useSubjects(Boolean(token));

  const activeSubjectName = (subjectsQuery.data || []).find((subject) => subject.id === subjectId)?.name;

  if (!subjectId) {
    return (
      <Card>
        <CardHeader>
          <Badge className="w-fit" variant="warning">
            Subject Required
          </Badge>
          <CardTitle>Select a subject first</CardTitle>
          <CardDescription>Go to Subjects and enter one subject to unlock all features.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button asChild>
            <Link href="/dashboard">
              <ArrowLeft className="size-4" />
              Open Subjects Directory
            </Link>
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="mx-auto grid w-full max-w-6xl gap-6">
      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <Badge className="w-fit">Inside Subject</Badge>
          <CardTitle className="text-2xl text-[var(--sl-text-primary)]">{activeSubjectName || "Selected Subject"}</CardTitle>
          <CardDescription className="text-[var(--sl-text-secondary)]">This is your subject workspace. Upload a document, then generate assets and chat with grounded context.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <Badge variant="success">Subject selected</Badge>
          <Badge variant={documentId ? "success" : "outline"}>{documentId ? "Document selected" : "No document selected"}</Badge>
        </CardContent>
      </Card>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <FileUp className="size-4 text-[var(--sl-lavender)]" />
              Upload Document
            </CardTitle>
            <CardDescription>Add a PDF/text source for this subject.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild size="sm" className="rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]">
              <Link href="/documents">Manage Documents</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="size-4 text-[var(--sl-lavender)]" />
              Generate
            </CardTitle>
            <CardDescription>Create flashcards and quiz questions.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild size="sm" variant="secondary">
              <Link href="/generate">Open Generate</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <MessageCircle className="size-4 text-[var(--sl-lavender)]" />
              Chat
            </CardTitle>
            <CardDescription>Ask grounded questions over your material.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild size="sm" variant="outline">
              <Link href="/chat">Open Chat</Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Timer className="size-4 text-[var(--sl-lavender)]" />
              History
            </CardTitle>
            <CardDescription>Review generated outputs for this scope.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild size="sm" variant="ghost">
              <Link href="/history">Open History</Link>
            </Button>
          </CardContent>
        </Card>
      </section>

      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardContent className="flex items-center justify-between gap-3 pt-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <BookOpenText className="size-4 text-[var(--sl-lavender)]" />
            Switch subjects anytime from the Subjects directory.
          </div>
          <Button asChild variant="outline" size="sm">
            <Link href="/dashboard">Back to Subjects</Link>
          </Button>
        </CardContent>
      </Card>

      <SubjectDocumentsManager />
    </div>
  );
}
