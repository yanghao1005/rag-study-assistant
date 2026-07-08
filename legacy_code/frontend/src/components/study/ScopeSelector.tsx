import { useState, useEffect } from "react";
import { useSubjectStore } from "@/lib/store/subjectStore";
import { useDocumentStore } from "@/lib/store/documentStore";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { BookOpen, FileText } from "lucide-react";

export interface StudyScope {
  mode: 'subject' | 'document';
  subjectId: string;
  documentId?: string;
}

interface ScopeSelectorProps {
  onScopeChange: (scope: StudyScope | null) => void;
  defaultSubjectId?: string;
}

export function ScopeSelector({ onScopeChange, defaultSubjectId }: ScopeSelectorProps) {
  const { subjects, fetchSubjects } = useSubjectStore();
  const { documents, fetchDocuments } = useDocumentStore();
  
  const [mode, setMode] = useState<'subject' | 'document'>('subject');
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>(defaultSubjectId || "");
  const [selectedDocumentId, setSelectedDocumentId] = useState<string>("");

  useEffect(() => {
    fetchSubjects();
  }, [fetchSubjects]);

  useEffect(() => {
    if (selectedSubjectId) {
      if (mode === 'document') {
        fetchDocuments(selectedSubjectId);
      }
      
      // Notify parent of valid config
      if (mode === 'subject') {
        onScopeChange({ mode: 'subject', subjectId: selectedSubjectId });
      } else if (mode === 'document' && selectedDocumentId) {
        onScopeChange({ mode: 'document', subjectId: selectedSubjectId, documentId: selectedDocumentId });
      } else {
        onScopeChange(null);
      }
    } else {
        onScopeChange(null);
    }
  }, [selectedSubjectId, selectedDocumentId, mode, fetchDocuments, onScopeChange]);

  const handleSubjectChange = (id: string) => {
    setSelectedSubjectId(id);
    setSelectedDocumentId(""); // Reset document when subject changes
  };

  return (
    <Card className="w-full">
      <CardContent className="p-6 space-y-6">
        <div className="space-y-2">
            <h3 className="text-lg font-medium">Study Scope</h3>
            <p className="text-sm text-muted-foreground">Select what you want to study today.</p>
        </div>

        <Tabs defaultValue="subject" value={mode} onValueChange={(v) => setMode(v as any)} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="subject" className="gap-2">
              <BookOpen className="h-4 w-4" />
              Entire Subject
            </TabsTrigger>
            <TabsTrigger value="document" className="gap-2">
              <FileText className="h-4 w-4" />
              Specific Document
            </TabsTrigger>
          </TabsList>

          <div className="mt-6 space-y-4">
            <div className="space-y-2">
              <Label>Subject</Label>
              <Select value={selectedSubjectId} onValueChange={handleSubjectChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a subject..." />
                </SelectTrigger>
                <SelectContent>
                  {subjects.length === 0 ? (
                    <div className="p-2 text-sm text-muted-foreground text-center">No subjects found</div>
                  ) : (
                      subjects.map(s => (
                        <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                      ))
                  )}
                </SelectContent>
              </Select>
            </div>

            <TabsContent value="document" className="mt-0 space-y-4">
              <div className="space-y-2">
                <Label>Document</Label>
                <Select 
                    value={selectedDocumentId} 
                    onValueChange={setSelectedDocumentId}
                    disabled={!selectedSubjectId}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={!selectedSubjectId ? "Select a subject first" : "Select a document..."} />
                  </SelectTrigger>
                  <SelectContent>
                     {documents.length === 0 ? (
                        <div className="p-2 text-sm text-muted-foreground text-center">No documents found</div>
                      ) : (
                          documents.map(d => (
                            <SelectItem key={d.id} value={d.id}>{d.filename}</SelectItem>
                          ))
                      )}
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </CardContent>
    </Card>
  );
}
