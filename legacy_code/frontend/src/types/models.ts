import type { Database } from '@/types/database.types';

type DbTables = Database['public']['Tables'];

type Override<T, U> = Omit<T, keyof U> & U;

export type DocumentType = Database['public']['Enums']['document_type'];
export type DocumentStatus = Database['public']['Enums']['document_status'];

export type Subject = Override<
  DbTables['subjects']['Row'],
  {
    description?: string;
    color?: string;
    document_count?: number;
    updated_at?: string;
  }
>;

export type Document = Override<
  DbTables['documents']['Row'],
  {
    file_size: number;
    total_pages?: number;
    content_text?: string;
    updated_at?: string;
  }
>;

export type Chapter = Override<
  DbTables['chapters']['Row'],
  {
    start_page: number;
    end_page: number;
    order_index: number;
  }
>;

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
