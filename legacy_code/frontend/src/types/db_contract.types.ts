// Thin contract layer derived from the canonical Supabase Database type.
// Keep this file import-stable for app modules that want simplified aliases.

import type { Database, Json } from '@/types/database.types'

export type { Database, Json }

export type AppRole = Database['public']['Enums']['app_role']
export type PlanTier = Database['public']['Enums']['plan_tier']
export type DocumentType = Database['public']['Enums']['document_type']
export type DocumentStatus = Database['public']['Enums']['document_status']
export type GeneratedType = Database['public']['Enums']['generated_type']
export type GenerationScope = Database['public']['Enums']['generation_scope']
export type UsageMetric = Database['public']['Enums']['usage_metric']

type Tables = Database['public']['Tables']

export type ProfilesRow = Tables['profiles']['Row']
export type SubjectsRow = Tables['subjects']['Row']
export type DocumentsRow = Tables['documents']['Row']
export type ChaptersRow = Tables['chapters']['Row']
export type DocumentChunksRow = Tables['document_chunks']['Row']
export type GeneratedContentRow = Tables['generated_content']['Row']
export type SubscriptionPlansRow = Tables['subscription_plans']['Row']
export type PlanLimitsRow = Tables['plan_limits']['Row']
export type UserSubscriptionsRow = Tables['user_subscriptions']['Row']
export type UsageEventsRow = Tables['usage_events']['Row']
export type BillingCustomersRow = Tables['billing_customers']['Row']

export type DbTables = {
  profiles: ProfilesRow
  subjects: SubjectsRow
  documents: DocumentsRow
  chapters: ChaptersRow
  document_chunks: DocumentChunksRow
  generated_content: GeneratedContentRow
  subscription_plans: SubscriptionPlansRow
  plan_limits: PlanLimitsRow
  user_subscriptions: UserSubscriptionsRow
  usage_events: UsageEventsRow
  billing_customers: BillingCustomersRow
}

export type TableName = keyof DbTables
