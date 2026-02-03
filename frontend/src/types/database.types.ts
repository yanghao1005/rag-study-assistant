export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      subjects: {
        Row: {
          id: string
          created_at: string
          name: string
          description: string | null
          color: string
          user_id: string
        }
        Insert: {
          id?: string
          created_at?: string
          name: string
          description?: string | null
          color?: string
          user_id?: string
        }
        Update: {
          id?: string
          created_at?: string
          name?: string
          description?: string | null
          color?: string
          user_id?: string
        }
      }
      documents: {
        Row: {
          id: string
          created_at: string
          subject_id: string
          filename: string
          file_path: string
          file_size: number
          status: 'processing' | 'ready' | 'error'
          document_type: 'pdf' | 'summary'
        }
        Insert: {
          id?: string
          created_at?: string
          subject_id: string
          filename: string
          file_path: string
          file_size: number
          status?: 'processing' | 'ready' | 'error'
          document_type?: 'pdf' | 'summary'
        }
        Update: {
          id?: string
          created_at?: string
          subject_id?: string
          filename?: string
          file_path?: string
          file_size?: number
          status?: 'processing' | 'ready' | 'error'
          document_type?: 'pdf' | 'summary'
        }
      }
      // Add other tables as needed based on the discussion
    }
  }
}
