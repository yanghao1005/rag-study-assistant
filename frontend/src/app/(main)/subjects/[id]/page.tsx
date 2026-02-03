"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { useSubjectStore } from "@/lib/store/subjectStore";
import { useDocumentStore } from "@/lib/store/documentStore";
import { Breadcrumb } from "@/components/common/Breadcrumb";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, BookOpen, Settings } from "lucide-react";
import { DocumentList } from "@/components/documents/DocumentList";
import { DocumentUploadModal } from "@/components/documents/DocumentUploadModal";
import { ConfirmDialog } from "@/components/shared/ConfirmDialog";
import { toast } from "sonner";
import { SubjectModal } from "@/components/subjects/SubjectModal";

export default function SubjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  
  const { subjects, fetchSubjectById, createSubject } = useSubjectStore();
  const { documents, isLoading, fetchDocuments, deleteDocument } = useDocumentStore();

  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isEditSubjectOpen, setIsEditSubjectOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState<string | null>(null);

  // Find subject from store or fetch
  const subject = subjects.find(s => s.id === id);

  useEffect(() => {
    // Ideally fetchSubjectById would populate the specific subject if not found
    // For now we assume subjects are loaded or we fetch them
    if (!subject) {
       // In a real app we would fetch the single subject here
       fetchSubjectById(id);
    }
    fetchDocuments(id);
  }, [id, subject, fetchSubjectById, fetchDocuments]);

  const handleDeleteDocument = (docId: string) => {
    setDocToDelete(docId);
  };

  const handleConfirmDelete = async () => {
    if (docToDelete) {
      await deleteDocument(docToDelete);
      setDocToDelete(null);
      toast.success("Document deleted");
    }
  };

  const handleEditSubject = async (data: any) => {
    // Placeholder for update logic
    toast.info("Subject updated (mock)");
    setIsEditSubjectOpen(false);
  };

  // Filter documents
  const pdfs = documents.filter(d => d.document_type === 'pdf');
  const summaries = documents.filter(d => d.document_type === 'summary');

  if (!subject) {
    return <div>Loading subject...</div>; // Or better skeleton
  }

  return (
    <div className="space-y-6">
      <Breadcrumb 
        items={[
          { label: "Subjects", href: "/subjects" },
          { label: subject.name }
        ]} 
      />

      {/* Header */}
      <div 
        className="rounded-xl p-6 text-white relative overflow-hidden shadow-lg"
        style={{ backgroundColor: subject.color || '#3B82F6' }}
      >
        <div className="relative z-10 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{subject.name}</h1>
            <p className="opacity-90 max-w-2xl">{subject.description}</p>
          </div>
          <Button 
            variant="secondary" 
            size="sm" 
            className="bg-white/20 hover:bg-white/30 text-white border-none"
            onClick={() => setIsEditSubjectOpen(true)}
          >
            <Settings className="h-4 w-4 mr-2" />
            Edit Subject
          </Button>
        </div>
        
        {/* Decorative background circle */}
        <div className="absolute -right-10 -bottom-20 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center">
        <Tabs defaultValue="all" className="w-[400px]">
          <TabsList>
            <TabsTrigger value="all">All Documents</TabsTrigger>
            <TabsTrigger value="pdfs">PDFs</TabsTrigger>
            <TabsTrigger value="summaries">Summaries</TabsTrigger>
          </TabsList>
        </Tabs>
        
        <div className="flex gap-2">
          <Button onClick={() => router.push(`/study?subject=${id}`)} variant="outline">
            <BookOpen className="h-4 w-4 mr-2" />
            Study Subject
          </Button>
          <Button onClick={() => setIsUploadOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Document
          </Button>
        </div>
      </div>

      {/* Content */}
      <Tabs defaultValue="all" className="w-full">
        {/* Note: The Tabs above are visual triggers, but here we render based on the same state if we managed it manually.
            However, Shadcn Tabs are controlled or uncontrolled. Since I separated the List triggers from content 
            visually in the layout (triggers on left, content below), I should technically wrap everything in one Tabs component 
            OR manage state manually. For simplicity, let's wrap the previous block and this block in one Tabs component if possible, 
            or use manual state.
            
            Let's use manual state for cleaner layout separation if needed, BUT for now, let's just use the Tabs structure correctly.
        */}
      </Tabs>
       {/* Correction: The TabsList was outside the TabsContent. Let's restructure properly. */}

       <Tabs defaultValue="all" className="w-full">
         <div className="flex justify-between items-center mb-6">
            <TabsList>
              <TabsTrigger value="all">All Documents ({documents.length})</TabsTrigger>
              <TabsTrigger value="pdfs">PDFs ({pdfs.length})</TabsTrigger>
              <TabsTrigger value="summaries">Summaries ({summaries.length})</TabsTrigger>
            </TabsList>

            <div className="flex gap-2">
              <Button onClick={() => router.push(`/study?subject=${id}`)} variant="outline">
                <BookOpen className="h-4 w-4 mr-2" />
                Study Subject
              </Button>
              <Button onClick={() => setIsUploadOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Document
              </Button>
            </div>
         </div>

         <TabsContent value="all" className="mt-0">
           <DocumentList 
             documents={documents} 
             isLoading={isLoading}
             onView={(docId) => console.log("View", docId)}
             onDelete={handleDeleteDocument}
           />
         </TabsContent>
         
         <TabsContent value="pdfs" className="mt-0">
            <DocumentList 
             documents={pdfs} 
             isLoading={isLoading}
             onView={(docId) => console.log("View", docId)}
             onDelete={handleDeleteDocument}
           />
         </TabsContent>

         <TabsContent value="summaries" className="mt-0">
            <DocumentList 
             documents={summaries} 
             isLoading={isLoading}
             onView={(docId) => console.log("View", docId)}
             onDelete={handleDeleteDocument}
           />
         </TabsContent>
       </Tabs>

      <DocumentUploadModal
        open={isUploadOpen}
        onOpenChange={setIsUploadOpen}
        subjectId={id}
      />

      <SubjectModal
        open={isEditSubjectOpen}
        onOpenChange={setIsEditSubjectOpen}
        onSubmit={handleEditSubject}
        initialData={subject}
        isLoading={false}
      />

      <ConfirmDialog
        open={!!docToDelete}
        onOpenChange={(open) => !open && setDocToDelete(null)}
        title="Delete Document"
        description="Are you sure you want to delete this document? This cannot be undone."
        onConfirm={handleConfirmDelete}
        confirmJson="Delete"
        variant="destructive"
      />
    </div>
  );
}
