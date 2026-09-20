import { Subject } from "@/types/models";
import { SubjectCard } from "./SubjectCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

interface SubjectGridProps {
  subjects: Subject[];
  isLoading: boolean;
  onView: (id: string) => void;
  onEdit: (subject: Subject) => void;
  onDelete: (id: string) => void;
  onCreate: () => void;
}

export function SubjectGrid({
  subjects,
  isLoading,
  onView,
  onEdit,
  onDelete,
  onCreate,
}: SubjectGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-[200px] w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (subjects.length === 0) {
    return (
      <div className="text-center py-12 border-2 border-dashed rounded-xl bg-muted/20">
        <h3 className="text-lg font-semibold mb-2">No subjects yet</h3>
        <p className="text-muted-foreground mb-6">
          Create your first subject to start organizing your study materials.
        </p>
        <Button onClick={onCreate}>
          <Plus className="h-4 w-4 mr-2" />
          Create Subject
        </Button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {subjects.map((subject) => (
        <SubjectCard
          key={subject.id}
          subject={subject}
          onView={onView}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
