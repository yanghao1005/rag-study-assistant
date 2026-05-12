"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { SubjectRequired } from "@/components/auth/subject-required";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { useSessionStore } from "@/features/auth/session-store";
import { useUploadDocument } from "@/features/documents/use-upload-document";
import { useJobStatus } from "@/features/jobs/use-job-status";

export default function NewDocumentPage() {
  const { token, subjectId, setDocumentId } = useSessionStore();
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState("");
  const [documentId, setLocalDocumentId] = useState("");

  const upload = useUploadDocument();
  const job = useJobStatus({ token, jobId, enabled: Boolean(token && jobId) });

  const normalizedStatus = (job.data?.status || "queued").toLowerCase();
  const progress = normalizedStatus === "completed" ? 100 : normalizedStatus === "running" ? 62 : normalizedStatus === "failed" ? 100 : 20;

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
      setJobId(payload.job_id || "");
      setLocalDocumentId(payload.document_id);
      setDocumentId(payload.document_id);
      toast.success("Upload queued successfully.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Upload failed.");
    }
  };

  return (
    <SubjectRequired>
      <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Document Upload</CardTitle>
          <CardDescription>Upload PDF, markdown, or text. Ingestion runs asynchronously in backend_v5 jobs.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="file">Document file</Label>
            <Input id="file" type="file" accept=".pdf,.txt,.md" onChange={(event) => setFile(event.target.files?.[0] || null)} />
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button disabled={upload.isPending} onClick={handleUpload}>
              {upload.isPending ? "Uploading..." : "Upload and Queue"}
            </Button>
            {documentId ? (
              <Button asChild variant="outline">
                <Link href={`/documents/${documentId}`}>Open Document Workspace</Link>
              </Button>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Ingestion Job</CardTitle>
          <CardDescription>Polling every 2 seconds until completion or failure.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3">
          <div className="flex items-center gap-2">
            <Badge variant="secondary">Job ID</Badge>
            <span className="font-mono text-xs text-muted-foreground">{jobId || "No job yet"}</span>
          </div>
          <Progress value={progress} />
          <div className="grid gap-2 text-sm">
            <p>
              <span className="text-muted-foreground">Status:</span> {job.data?.status || "-"}
            </p>
            <p>
              <span className="text-muted-foreground">Last error:</span> {job.data?.error_message || "none"}
            </p>
          </div>
        </CardContent>
      </Card>
      </div>
    </SubjectRequired>
  );
}
