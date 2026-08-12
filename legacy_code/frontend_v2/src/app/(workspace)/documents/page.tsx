import { SubjectRequired } from "@/components/auth/subject-required";
import { SubjectDocumentsManager } from "@/components/documents/subject-documents-manager";

export default function DocumentsPage() {
  return (
    <SubjectRequired>
      <SubjectDocumentsManager />
    </SubjectRequired>
  );
}

