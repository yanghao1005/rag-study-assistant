import { Subject, Document, Chapter } from './models';

// Subjects
export type CreateSubjectRequest = {
  name: string;
  description?: string;
  color?: string;
};
export type UpdateSubjectRequest = Partial<CreateSubjectRequest>;
export type SubjectResponse = Subject;

// Documents
// UploadDocumentRequest is handled via FormData

export type CreateSummaryRequest = {
  subject_id: string;
  title: string;
  content: string;
  chapter_id?: string;
};

export type DocumentResponse = Document & {
  chapters?: Chapter[];
};

// Generation
export type GenerationScope = 'subject' | 'document' | 'chapter' | 'summary';
export type PromptProfile = 'concise' | 'exam' | 'conceptual';

export type SourceCitation = {
  document_type?: 'pdf' | 'summary';
  page?: number | null;
  chapter_name?: string | null;
  preview?: string | null;
};

export type RetrievalDiagnostics = {
  scope: GenerationScope;
  scope_id: string;
  query: string;
  total_candidates: number;
  accepted_candidates: number;
  best_score: number;
  debug_trace_id?: string | null;
  debug_artifact_path?: string | null;
};

export type GenerateFlashcardsRequest = {
  scope: GenerationScope;
  scope_id: string;
  count: number;
  query?: string;
  user_id?: string;
  save?: boolean;
  prompt_profile?: PromptProfile;
  front_max_chars?: number;
  back_max_chars?: number;
  debug?: boolean;
};

export type GenerateQuizRequest = {
  scope: GenerationScope;
  scope_id: string;
  count: number;
  query?: string;
  user_id?: string;
  save?: boolean;
  prompt_profile?: PromptProfile;
  question_max_chars?: number;
  explanation_max_chars?: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  debug?: boolean;
};

export type GenerateFlashcardsResponse = {
  sources?: SourceCitation[];
  diagnostics?: RetrievalDiagnostics;
  flashcards: Array<{
    front: string;
    back: string;
  }>;
};

export type GenerateQuizResponse = {
  questions: Array<{
    question: string;
    options: string[];
    correct_answer: number;
    explanation: string;
    source?: SourceCitation;
  }>;
  diagnostics?: RetrievalDiagnostics;
};

export type GeneratedHistoryItem = {
  id: string;
  user_id: string;
  scope: GenerationScope;
  type: string;
  created_at?: string | null;
  subject_id?: string | null;
  document_id?: string | null;
  chapter_id?: string | null;
  content_json: Record<string, unknown>;
};

export type GeneratedHistoryResponse = {
  items: GeneratedHistoryItem[];
};

// Error
export type ApiErrorResponse = {
  error: string;
  message: string;
  details?: Record<string, unknown>;
};
