import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { FileUpload } from "./FileUpload";
import { useDocumentStore } from "@/lib/store/documentStore";
import { toast } from "sonner";

interface DocumentUploadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  subjectId: string;
}

// Validation Schema for Summary
const summarySchema = z.object({
  title: z.string().min(1, "Title is required").max(100),
  content: z.string().min(100, "Summary must be at least 100 characters").max(50000),
});

type SummaryFormValues = z.infer<typeof summarySchema>;

export function DocumentUploadModal({
  open,
  onOpenChange,
  subjectId,
}: DocumentUploadModalProps) {
  const [activeTab, setActiveTab] = useState("pdf");
  const { uploadPdf, createSummary, isUploading } = useDocumentStore();
  
  // PDF Upload State
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Summary Form
  const form = useForm<SummaryFormValues>({
    resolver: zodResolver(summarySchema),
    defaultValues: {
      title: "",
      content: "",
    },
  });

  const handlePdfUpload = async () => {
    if (!pdfFile) return;

    try {
      // Simulate progress for now since XHR progress isn't hooked up deeply yet
      const interval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      await uploadPdf(subjectId, pdfFile);
      
      clearInterval(interval);
      setUploadProgress(100);
      toast.success("PDF uploaded successfully");
      onOpenChange(false);
      setPdfFile(null);
      setUploadProgress(0);
    } catch (error) {
      toast.error("Failed to upload PDF");
      setUploadProgress(0);
    }
  };

  const handleSummarySubmit = async (data: SummaryFormValues) => {
    try {
      await createSummary(subjectId, data.title, data.content);
      toast.success("Summary created successfully");
      form.reset();
      onOpenChange(false);
    } catch (error) {
      toast.error("Failed to create summary");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-150">
        <DialogHeader>
          <DialogTitle>Add Document</DialogTitle>
          <DialogDescription>
            Upload a PDF or write a text summary for this subject.
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="pdf">Upload PDF</TabsTrigger>
            <TabsTrigger value="summary">Create Summary</TabsTrigger>
          </TabsList>

          <TabsContent value="pdf" className="space-y-4 py-4">
            <FileUpload 
              onFileSelect={setPdfFile} 
              isUploading={isUploading}
              progress={uploadProgress}
            />
            <div className="flex justify-end">
              <Button 
                onClick={handlePdfUpload} 
                disabled={!pdfFile || isUploading}
              >
                {isUploading ? "Uploading…" : "Upload PDF"}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="summary" className="py-4">
            <Form {...form}>
              <form onSubmit={form.handleSubmit(handleSummarySubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Title</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Chapter 1 Summary" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="content"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Content</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder="Write your summary here..." 
                          className="min-h-50"
                          {...field} 
                        />
                      </FormControl>
                      <div className="text-xs text-muted-foreground text-right">
                        {field.value.length} / 50000 characters (min 100)
                      </div>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="flex justify-end">
                  <Button type="submit" disabled={isUploading}>
                    {isUploading ? "Saving…" : "Save Summary"}
                  </Button>
                </div>
              </form>
            </Form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
