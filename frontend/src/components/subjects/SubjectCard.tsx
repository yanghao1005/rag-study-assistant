import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Book, Edit, Trash2 } from "lucide-react";
import { Subject } from "@/types/models";
import { format } from "date-fns";

interface SubjectCardProps {
  subject: Subject;
  onView: (id: string) => void;
  onEdit: (subject: Subject) => void;
  onDelete: (id: string) => void;
}

export function SubjectCard({ subject, onView, onEdit, onDelete }: SubjectCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow relative overflow-hidden group">
      <div 
        className="absolute top-0 left-0 w-1.5 h-full" 
        style={{ backgroundColor: subject.color || '#3B82F6' }}
      />
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-xl mb-1 cursor-pointer hover:text-primary" onClick={() => onView(subject.id)}>
              {subject.name}
            </CardTitle>
            <CardDescription className="line-clamp-2 min-h-[40px]">
              {subject.description || "No description provided."}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardFooter className="flex justify-between items-center text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Book className="h-4 w-4" />
          <span>{subject.document_count || 0} Documents</span>
        </div>
        
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button variant="ghost" size="icon" onClick={() => onEdit(subject)}>
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive" onClick={() => onDelete(subject.id)}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
