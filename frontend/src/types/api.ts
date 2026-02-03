import { Subject, Document, Chapter, Flashcard, QuizQuestion, DocumentType } from './models';

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

export type GenerateFlashcardsRequest = {
  scope: GenerationScope;
  scope_id: string;
  count: number;
  query?: string;
};

export type GenerateQuizRequest = {
  scope: GenerationScope;
  scope_id: string;
  count: number;
  difficulty?: 'easy' | 'medium' | 'hard';
};

export type GenerateFlashcardsResponse = {
  flashcards: Flashcard[];
};

export type GenerateQuizResponse = {
  questions: QuizQuestion[];
};

// Error
export type ApiErrorResponse = {
  error: string;
  message: string;
  details?: Record<string, unknown>;
};
