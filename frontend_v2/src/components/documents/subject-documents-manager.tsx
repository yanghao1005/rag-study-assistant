"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Pencil, Trash2 } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { useSessionStore } from "@/features/auth/session-store";
import {
  documentsQueryKey,
  useDeleteDocument,
  useRenameDocument,
  useSubjectDocuments,
} from "@/features/documents/use-subject-documents";
import { useUploadDocument } from "@/features/documents/use-upload-document";
import { useJobStatus } from "@/features/jobs/use-job-status";
import type { DocumentRecord } from "@/lib/schemas/backend";

function formatBytes(value: number): string {
  if (!value || value <= 0) {
    return "0 B";
  }
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function statusBadgeVariant(status: string): "success" | "warning" | "outline" | "secondary" {
  const normalized = status.toLowerCase();
  if (normalized === "ready" || normalized === "completed") {
    return "success";
  }
  if (normalized === "error" || normalized === "failed") {
    return "warning";
  }
  if (normalized === "processing" || normalized === "queued" || normalized === "running") {
    return "secondary";
  }
  return "outline";
}

export function SubjectDocumentsManager() {
  const queryClient = useQueryClient();
  const { token, subjectId, setDocumentId } = useSessionStore();
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState("");
  const [editingId, setEditingId] = useState("");
  const [editingName, setEditingName] = useState("");

  const upload = useUploadDocument();
  const documents = useSubjectDocuments({ token, subjectId, enabled: Boolean(token && subjectId) });
  const rename = useRenameDocument(subjectId);
  const remove = useDeleteDocument(subjectId);
  const job = useJobStatus({ token, jobId, enabled: Boolean(token && jobId) });

  const normalizedStatus = (job.data?.status || "queued").toLowerCase();
  const progress = normalizedStatus === "completed" ? 100 : normalizedStatus === "running" ? 62 : normalizedStatus === "failed" ? 100 : 20;

  const items = useMemo(() => documents.data?.items || [], [documents.data?.items]);

  const startRename = (item: DocumentRecord) => {
    setEditingId(item.id);
    setEditingName(item.filename);
  };

  const handleRename = async (documentId: string) => {
    const nextName = editingName.trim();
    if (!token) {
      toast.error("Token is required.");
      return;
    }
    if (!nextName) {
      toast.error("Filename cannot be empty.");
      return;
    }

    try {
      await rename.mutateAsync({ token, documentId, filename: nextName });
      toast.success("Document name updated.");
      setEditingId("");
      setEditingName("");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Rename failed.");
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!token) {
      toast.error("Token is required.");
      return;
    }

    const confirmed = window.confirm("Delete this document? This action cannot be undone.");
    if (!confirmed) {
      return;
    }

    try {
      await remove.mutateAsync({ token, documentId });
      toast.success("Document deleted.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Delete failed.");
    }
  };

  const handleUpload = async () => {
    if (!token) {
      toast.error("Token is required.");
      return;
    }
    if (!subjectId) {
      toast.error("Subject ID is required.");
      return;
    }
    if (!file) {
      toast.error("Select a file first.");
      return;
    }

    try {
      const payload = await upload.mutateAsync({ token, subjectId, file });
      setDocumentId(payload.document_id);
      setJobId(payload.job_id || "");
      setFile(null);
      void queryClient.invalidateQueries({ queryKey: documentsQueryKey(subjectId) });
      toast.success("Upload queued successfully.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Upload failed.");
    }
  };

  return (
    <div className="grid gap-6">
      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <CardTitle>Upload to Current Subject</CardTitle>
          <CardDescription>Attach a PDF/text file and queue ingestion in backend_v5.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="subject-document-file">Document file</Label>
            <Input
              id="subject-document-file"
              type="file"
              accept=".pdf,.txt,.md"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button
              disabled={upload.isPending}
              onClick={handleUpload}
              className="rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]"
            >
              {upload.isPending ? "Uploading..." : "Upload and Queue"}
            </Button>
            <Button type="button" variant="outline" onClick={() => documents.refetch()}>
              Refresh List
            </Button>
          </div>
        </CardContent>
      </Card>

      {jobId ? (
        <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
          <CardHeader>
            <CardTitle>Latest Ingestion Job</CardTitle>
            <CardDescription>Polling every 2 seconds until completion or failure.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">Job ID</Badge>
              <span className="font-mono text-xs text-muted-foreground">{jobId}</span>
            </div>
            <Progress value={progress} />
            <div className="grid gap-1 text-sm">
              <p>
                <span className="text-muted-foreground">Status:</span> {job.data?.status || "-"}
              </p>
              <p>
                <span className="text-muted-foreground">Last error:</span> {job.data?.error_message || "none"}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : null}

      <Card className="border-[var(--sl-muted)] bg-white shadow-sl-sm">
        <CardHeader>
          <CardTitle>Documents in This Subject</CardTitle>
          <CardDescription>List and manage all uploaded documents tied to the current subject.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3">
          {documents.isLoading ? <p className="text-sm text-muted-foreground">Loading documents...</p> : null}

          {!documents.isLoading && items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No documents yet for this subject.</p>
          ) : null}

          {items.map((item) => (
            <div key={item.id} className="rounded-sl-standard border border-[var(--sl-muted)] p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="min-w-0 space-y-1">
                  <p className="truncate text-sm font-medium text-[var(--sl-text-primary)]">{item.filename}</p>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <Badge variant={statusBadgeVariant(item.status)}>{item.status}</Badge>
                    <span>{item.document_type.toUpperCase()}</span>
                    <span>{formatBytes(item.file_size)}</span>
                  </div>
                  {item.error_message ? <p className="text-xs text-[var(--sl-rose)]">{item.error_message}</p> : null}
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <Button asChild size="sm" variant="outline" onClick={() => setDocumentId(item.id)}>
                    <Link href={`/documents/${item.id}`}>Open</Link>
                  </Button>
                  <Button type="button" size="sm" variant="ghost" onClick={() => startRename(item)}>
                    <Pencil className="size-4" />
                    Rename
                  </Button>
                  <Button type="button" size="sm" variant="destructive" onClick={() => handleDelete(item.id)}>
                    <Trash2 className="size-4" />
                    Delete
                  </Button>
                </div>
              </div>

              {editingId === item.id ? (
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Input value={editingName} onChange={(event) => setEditingName(event.target.value)} className="max-w-sm" />
                  <Button type="button" size="sm" onClick={() => handleRename(item.id)} disabled={rename.isPending}>
                    Save
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setEditingId("");
                      setEditingName("");
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              ) : null}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
