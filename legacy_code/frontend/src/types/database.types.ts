export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      billing_customers: {
        Row: {
          created_at: string
          id: string
          provider: string
          provider_customer_id: string
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          provider?: string
          provider_customer_id: string
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          provider?: string
          provider_customer_id?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: 'billing_customers_user_id_fkey'
            columns: ['user_id']
            isOneToOne: true
            referencedRelation: 'profiles'
            referencedColumns: ['id']
          }
        ]
      }
      chapters: {
        Row: {
          created_at: string
          document_id: string
          end_page: number | null
          id: string
          name: string
          order_index: number | null
          start_page: number | null
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          document_id: string
          end_page?: number | null
          id?: string
          name: string
          order_index?: number | null
          start_page?: number | null
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          document_id?: string
          end_page?: number | null
          id?: string
          name?: string
          order_index?: number | null
          start_page?: number | null
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: 'chapters_document_id_fkey'
            columns: ['document_id']
            isOneToOne: false
            referencedRelation: 'documents'
            referencedColumns: ['id']
          },
          {
            foreignKeyName: 'chapters_user_id_fkey'
            columns: ['user_id']
            isOneToOne: false
            referencedRelation: 'profiles'
            referencedColumns: ['id']
          }
        ]
      }
      document_chunks: {
        Row: {
          chapter_id: string | null
          content: string
          created_at: string
          document_id: string
          embedding: string
          id: string
          metadata: Json
          user_id: string
        }
        Insert: {
          chapter_id?: string | null
          content: string
          created_at?: string
          document_id: string
          embedding: string
          id?: string
          metadata?: Json
          user_id: string
        }
        Update: {
          chapter_id?: string | null
          content?: string
          created_at?: string
          document_id?: string
          embedding?: string
          id?: string
          metadata?: Json
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: 'document_chunks_chapter_id_fkey'
            columns: ['chapter_id']
            isOneToOne: false
            referencedRelation: 'chapters'
            referencedColumns: ['id']
          },
          {
            foreignKeyName: 'document_chunks_document_id_fkey'
            columns: ['document_id']
            isOneToOne: false
            referencedRelation: 'documents'
            referencedColumns: ['id']
          },
          {
            foreignKeyName: 'document_chunks_user_id_fkey'
            columns: ['user_id']
            isOneToOne: false
            referencedRelation: 'profiles'
            referencedColumns: ['id']
          }
        ]
      }
      documents: {
        Row: {
          content_text: string | null
          created_at: string
          document_type: Database['public']['Enums']['document_type']
          error_message: string | null
          file_size: number | null
          filename: string
          id: string
          status: Database['public']['Enums']['document_status']
          subject_id: string
          total_pages: number | null
          updated_at: string
          user_id: string
        }
        Insert: {
          content_text?: string | null
          created_at?: string
          document_type?: Database['public']['Enums']['document_type']
          error_message?: string | null
          file_size?: number | null
          filename: string
          id?: string
          status?: Database['public']['Enums']['document_status']
          subject_id: string
          total_pages?: number | null
          updated_at?: string
          user_id: string
        }
        Update: {
          content_text?: string | null
          created_at?: string
          document_type?: Database['public']['Enums']['document_type']
          error_message?: string | null
          file_size?: number | null
          filename?: string
          id?: string
          status?: Database['public']['Enums']['document_status']
          subject_id?: string
          total_pages?: number | null
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: 'documents_subject_id_fkey'
            columns: ['subject_id']
            isOneToOne: false
            referencedRelation: 'subjects'
            referencedColumns: ['id']
          },
          {
            foreignKeyName: 'documents_user_id_fkey'
            columns: ['user_id']
            isOneToOne: false
            referencedRelation: 'profiles'
            referencedColumns: ['id']
          }
        ]
      }
      generated_content: {
        Row: {
          chapter_id: string | null
          content_json: Json
          created_at: string
          document_id: string | null
          id: string
          scope: Database['public']['Enums']['generation_scope']
          subject_id: string | null
          type: Database['public']['Enums']['generated_type']
          user_id: string
        }
        Insert: {
          chapter_id?: string | null
          content_json: Json
          created_at?: string
          document_id?: string | null
          id?: string
          scope: Database['public']['Enums']['generation_scope']
          subject_id?: string | null
          type: Database['public']['Enums']['generated_type']
          user_id: string
        }
        Update: {
          chapter_id?: string | null
          content_json?: Json
          created_at?: string
          document_id?: string | null
          id?: string
          scope?: Database['public']['Enums']['generation_scope']
          subject_id?: string | null
          type?: Database['public']['Enums']['generated_type']
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: 'generated_content_chapter_id_fkey'
            columns: ['chapter_id']
            isOneToOne: false
            referencedRelation: 'chapters'
            referencedColumns: ['id']
          },
          {
            foreignKeyName: 'generated_content_document_id_fkey'
            columns: ['document_id']
            isOneToOne: false
            referencedRelation: 'documents'
            referencedColumns: ['id']
          },
          {
            foreignKeyName: 'generated_content_subject_id_fkey'
            columns: ['subject_id']
            isOneToOne: false
            referencedRelation: 'subjects'
            referencedColumns: ['id']
          },
          {
            foreignKeyName: 'generated_content_user_id_fkey'
            columns: ['user_id']
            isOneToOne: false
            referencedRelation: 'profiles'
            referencedColumns: ['id']
          }
        ]
      }
      plan_limits: {
        Row: {
          created_at: string
          id: string
          metric: Database['public']['Enums']['usage_metric']
          monthly_limit: number | null
          plan_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          metric: Database['public']['Enums']['usage_metric']
          monthly_limit?: number | null
          plan_id: string
        }
        Update: {
          created_at?: string
          id?: string
          metric?: Database['public']['Enums']['usage_metric']
          monthly_limit?: number | null
          plan_id?: string
        }
        Relationships: [
          {
            foreignKeyName: 'plan_limits_plan_id_fkey'
            columns: ['plan_id']
            isOneToOne: false
            referencedRelation: 'subscription_plans'
            referencedColumns: ['id']
          }
        ]
      }
      profiles: {
        Row: {
          created_at: string
          email: string | null
          full_name: string | null
          id: string
          is_active: boolean
          role: Database['public']['Enums']['app_role']
          updated_at: string
        }
        Insert: {
          created_at?: string
          email?: string | null
          full_name?: string | null
          id: string
          is_active?: boolean
          role?: Database['public']['Enums']['app_role']
          updated_at?: string
        }
        Update: {
          created_at?: string
          email?: string | null
          full_name?: string | null
          id?: string
          is_active?: boolean
          role?: Database['public']['Enums']['app_role']
          updated_at?: string
        }
        Relationships: []
      }
      subjects: {
        Row: {
          color: string | null
          created_at: string
          description: string | null
          id: string
          name: string
          updated_at: string
          user_id: string
        }
        Insert: {
          color?: string | null
          created_at?: string
          description?: string | null
          id?: string
          name: string
          updated_at?: string
          user_id: string
        }
        Update: {
          color?: string | null
          created_at?: string
          description?: string | null
          id?: string
          name?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: 'subjects_user_id_fkey'
            columns: ['user_id']
            isOneToOne: false
            referencedRelation: 'profiles'
            referencedColumns: ['id']
          }
        ]
      }
      subscription_plans: {
        Row: {
          active: boolean
          created_at: string
          id: string
          monthly_price_cents: number
          name: string
          tier: Database['public']['Enums']['plan_tier']
          updated_at: string
        }
        Insert: {
          active?: boolean
          created_at?: string
          id?: string
          monthly_price_cents?: number
          name: string
          tier: Database['public']['Enums']['plan_tier']
          updated_at?: string
        }
        Update: {
          active?: boolean
          created_at?: string
          id?: string
          monthly_price_cents?: number
          name?: string
          tier?: Database['public']['Enums']['plan_tier']
          updated_at?: string
        }
        Relationships: []
      }
      usage_events: {
        Row: {
          amount: number
          created_at: string
          id: string
          metadata: Json
          metric: Database['public']['Enums']['usage_metric']
          period_start: string
          source: string | null
          user_id: string
        }
        Insert: {
          amount?: number
          created_at?: string
          id?: string
          metadata?: Json
          metric: Database['public']['Enums']['usage_metric']
          period_start: string
          source?: string | null
          user_id: string
        }
        Update: {
          amount?: number
          created_at?: string
          id?: string
          metadata?: Json
          metric?: Database['public']['Enums']['usage_metric']
          period_start?: string
          source?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: 'usage_events_user_id_fkey'
            columns: ['user_id']
            isOneToOne: false
            referencedRelation: 'profiles'
            referencedColumns: ['id']
          }
        ]
      }
      user_subscriptions: {
        Row: {
          cancel_at_period_end: boolean
          created_at: string
          current_period_end: string
          current_period_start: string
          id: string
          plan_id: string
          provider_subscription_id: string | null
          status: string
          updated_at: string
          user_id: string
        }
        Insert: {
          cancel_at_period_end?: boolean
          created_at?: string
          current_period_end: string
          current_period_start: string
          id?: string
          plan_id: string
          provider_subscription_id?: string | null
          status?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          cancel_at_period_end?: boolean
          created_at?: string
          current_period_end?: string
          current_period_start?: string
          id?: string
          plan_id?: string
          provider_subscription_id?: string | null
          status?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: 'user_subscriptions_plan_id_fkey'
            columns: ['plan_id']
            isOneToOne: false
            referencedRelation: 'subscription_plans'
            referencedColumns: ['id']
          },
          {
            foreignKeyName: 'user_subscriptions_user_id_fkey'
            columns: ['user_id']
            isOneToOne: false
            referencedRelation: 'profiles'
            referencedColumns: ['id']
          }
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      check_and_consume_quota: {
        Args: {
          p_amount?: number
          p_metadata?: Json
          p_metric: Database['public']['Enums']['usage_metric']
          p_source?: string
        }
        Returns: {
          allowed: boolean
          quota_limit: number | null
          reason: string
          remaining: number
          used: number
        }[]
      }
      current_period_start: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      ensure_current_profile: {
        Args: Record<PropertyKey, never>
        Returns: boolean
      }
      get_effective_plan: {
        Args: { p_user_id: string }
        Returns: Database['public']['Enums']['plan_tier']
      }
      get_monthly_limit: {
        Args: {
          p_metric: Database['public']['Enums']['usage_metric']
          p_user_id: string
        }
        Returns: number | null
      }
      get_usage_amount: {
        Args: {
          p_metric: Database['public']['Enums']['usage_metric']
          p_period_start?: string
          p_user_id: string
        }
        Returns: number
      }
      is_admin: {
        Args: { p_user_id?: string }
        Returns: boolean
      }
      match_document_chunks: {
        Args: {
          filter_chapter_id?: string
          filter_document_id?: string
          filter_subject_id?: string
          filter_user_id?: string
          match_count?: number
          match_threshold?: number
          query_embedding: string
        }
        Returns: {
          chapter_id: string | null
          content: string
          document_id: string
          id: string
          metadata: Json
          similarity: number
          user_id: string
        }[]
      }
    }
    Enums: {
      app_role: 'student' | 'admin'
      document_status: 'processing' | 'ready' | 'error'
      document_type: 'pdf' | 'summary'
      generated_type: 'flashcard' | 'quiz'
      generation_scope: 'subject' | 'document' | 'chapter' | 'summary'
      plan_tier: 'free' | 'pro' | 'enterprise'
      usage_metric:
        | 'upload_requests'
        | 'flashcard_requests'
        | 'quiz_requests'
        | 'embedding_tokens'
        | 'generation_tokens'
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}
