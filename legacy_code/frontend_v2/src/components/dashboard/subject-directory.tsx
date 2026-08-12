"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { BookOpen, FolderOpen, PlusCircle } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSessionStore } from "@/features/auth/session-store";
import { useCreateSubject, useSubjects } from "@/features/subjects/use-subjects";
import { cn } from "@/lib/utils/cn";

export function SubjectDirectory() {
  const router = useRouter();
  const { token, subjectId, setSubjectId, setDocumentId } = useSessionStore();
  const [newSubjectName, setNewSubjectName] = useState("");

  const subjectsQuery = useSubjects(Boolean(token));
  const createSubject = useCreateSubject();

  const hasSubjects = (subjectsQuery.data || []).length > 0;

  const currentSubjectName = useMemo(() => {
    const subjects = subjectsQuery.data || [];
    return subjects.find((subject) => subject.id === subjectId)?.name || "";
  }, [subjectId, subjectsQuery.data]);

  const handleCreateSubject = () => {
    if (!newSubjectName.trim()) {
      toast.error("Enter a subject name first.");
      return;
    }

    createSubject.mutate(newSubjectName, {
      onSuccess: (subject) => {
        setSubjectId(subject.id);
        setDocumentId("");
        setNewSubjectName("");
        toast.success(`Subject created: ${subject.name}`);
        router.push("/subject");
      },
      onError: (error) => {
        toast.error(error instanceof Error ? error.message : "Failed to create subject.");
      },
    });
  };

  const handleEnterSubject = (id: string) => {
    setSubjectId(id);
    setDocumentId("");
    router.push("/subject");
  };

  return (
    <div className="mx-auto grid w-full max-w-6xl gap-6">
      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <Badge className="w-fit">Subjects</Badge>
          <CardTitle className="text-2xl text-[var(--sl-text-primary)]">Subject Directory</CardTitle>
          <CardDescription className="text-[var(--sl-text-secondary)]">Select a subject to enter its workspace. All features unlock inside the selected subject.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
          <div className="grid gap-2">
            <Label htmlFor="new-subject">Create new subject</Label>
            <Input
              id="new-subject"
              value={newSubjectName}
              onChange={(event) => setNewSubjectName(event.target.value)}
              placeholder="Example: Biology 101"
            />
          </div>
          <Button type="button" onClick={handleCreateSubject} disabled={createSubject.isPending} className="rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]">
            <PlusCircle className="size-4" />
            {createSubject.isPending ? "Creating..." : "Create and Enter"}
          </Button>
        </CardContent>
      </Card>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {(subjectsQuery.data || []).map((subject) => {
          const isActive = subject.id === subjectId;
          return (
            <Card key={subject.id} className={cn("border-[var(--sl-muted)] bg-white shadow-sl-sm", isActive ? "border-[var(--sl-lavender)]" : undefined)}>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <BookOpen className="size-4 text-[var(--sl-lavender)]" />
                  {subject.name}
                </CardTitle>
                <CardDescription>{isActive ? "Current selected subject" : "Subject workspace ready"}</CardDescription>
              </CardHeader>
              <CardContent className="flex items-center justify-between gap-2">
                <Badge variant={isActive ? "success" : "outline"}>{isActive ? "Active" : "Available"}</Badge>
                <Button type="button" size="sm" onClick={() => handleEnterSubject(subject.id)} className="rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]">
                  <FolderOpen className="size-4" />
                  Enter Subject
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </section>

      {!hasSubjects ? (
        <Card className="border-dashed border-[var(--sl-muted)] bg-white">
          <CardContent className="pt-6 text-sm text-muted-foreground">
            No subjects yet. Create your first subject above, then enter it to access upload, generate, chat, and history.
          </CardContent>
        </Card>
      ) : null}

      {currentSubjectName ? (
        <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
          <CardContent className="flex flex-wrap items-center justify-between gap-3 pt-6">
            <p className="text-sm text-muted-foreground">
              Current subject: <span className="font-medium text-foreground">{currentSubjectName}</span>
            </p>
            <Button type="button" variant="secondary" className="rounded-sl-standard" onClick={() => router.push("/subject")}>Enter Current Subject Workspace</Button>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
