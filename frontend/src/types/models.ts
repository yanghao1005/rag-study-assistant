export type Subject = {
  id: string;
  name: string;
  description?: string;
  color?: string;
  document_count?: number;
  created_at: string;
  updated_at?: string;
};

export type DocumentType = 'pdf' | 'summary';
export type DocumentStatus = 'processing' | 'ready' | 'error';

export type Document = {
  id: string;
  subject_id: string;
  document_type: DocumentType;
  filename: string;
  file_size: number;
  status: DocumentStatus;
  total_pages?: number;
  content_text?: string; // For summaries
  created_at: string;
  updated_at?: string;
};

export type Chapter = {
  id: string;
  document_id: string;
  name: string;
  start_page: number;
  end_page: number;
  order_index: number;
};

export type SourceInfo = {
  document: string;
  document_type: DocumentType;
  document_id?: string;
  page?: number;
  chapter?: string;
};

export type Flashcard = {
  id: string;
  front: string;
  back: string;
  source?: SourceInfo;
};

export type QuizQuestion = {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  source?: SourceInfo;
};
