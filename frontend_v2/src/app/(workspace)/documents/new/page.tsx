"use client";

import { SubjectRequired } from "@/components/auth/subject-required";
import { SubjectDocumentsManager } from "@/components/documents/subject-documents-manager";

export default function NewDocumentPage() {
  return (
    <SubjectRequired>
      <div className="mx-auto grid w-full max-w-6xl gap-6">
        <SubjectDocumentsManager />
      </div>
    </SubjectRequired>
  );
}
