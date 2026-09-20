"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSubjectStore } from "@/lib/store/subjectStore";
import { SubjectGrid } from "@/components/subjects/SubjectGrid";
import { SubjectModal } from "@/components/subjects/SubjectModal";
import { ConfirmDialog } from "@/components/shared/ConfirmDialog";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { Subject } from "@/types/models";
import { toast } from "sonner";
import { Breadcrumb } from "@/components/common/Breadcrumb";

export default function SubjectsPage() {
  const router = useRouter();
  const { subjects, isLoading, fetchSubjects, createSubject, deleteSubject } = useSubjectStore();
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<Subject | undefined>(undefined);
  const [subjectToDelete, setSubjectToDelete] = useState<string | null>(null);

  useEffect(() => {
    fetchSubjects();
  }, [fetchSubjects]);

  const handleCreate = () => {
    setEditingSubject(undefined);
    setIsModalOpen(true);
  };

  const handleEdit = (subject: Subject) => {
    setEditingSubject(subject);
    setIsModalOpen(true);
  };

  const handleDeleteClick = (id: string) => {
    setSubjectToDelete(id);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (subjectToDelete) {
      await deleteSubject(subjectToDelete);
      setIsDeleteDialogOpen(false);
      setSubjectToDelete(null);
      toast.success("Subject deleted successfully");
    }
  };

  const handleModalSubmit = async (data: any) => {
    try {
      if (editingSubject) {
        // Update logic would go here if/when update is implemented in store
         toast.info("Update feature coming soon!");
      } else {
        await createSubject(data);
        toast.success("Subject created successfully");
      }
      setIsModalOpen(false);
    } catch (error) {
      toast.error("Failed to save subject");
    }
  };

  return (
    <div className="space-y-6">
      <Breadcrumb items={[{ label: "Subjects" }]} />
      
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Subjects</h1>
          <p className="text-muted-foreground mt-1">
            Manage your courses and study materials.
          </p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="mr-2 h-4 w-4" />
          New Subject
        </Button>
      </div>

      <SubjectGrid 
        subjects={subjects}
        isLoading={isLoading}
        onView={(id) => router.push(`/subjects/${id}`)}
        onEdit={handleEdit}
        onDelete={handleDeleteClick}
        onCreate={handleCreate}
      />

      <SubjectModal
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
        onSubmit={handleModalSubmit}
        initialData={editingSubject}
        isLoading={isLoading}
      />

      <ConfirmDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        title="Delete Subject"
        description="Are you sure you want to delete this subject? This will permanently delete all associated documents and study materials."
        onConfirm={handleConfirmDelete}
        confirmJson="Delete Subject"
        variant="destructive"
      />
    </div>
  );
}
