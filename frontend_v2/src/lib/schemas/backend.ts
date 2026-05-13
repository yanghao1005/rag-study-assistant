import { z } from "zod";

export const scopeLiteralSchema = z.enum(["subject", "document", "chapter", "summary"]);

export const documentUploadResponseSchema = z.object({
  document_id: z.string(),
  filename: z.string(),
  file_path: z.string(),
  status: z.string(),
  job_id: z.string().nullable().optional(),
});

export const stageRunSchema = z.object({
  id: z.string().optional(),
  stage: z.string(),
  status: z.string(),
  duration_ms: z.number().optional(),
  details: z.record(z.any()).optional(),
  created_at: z.string().optional(),
});

export const jobSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  job_type: z.string(),
  status: z.string(),
  payload: z.record(z.any()).optional(),
  result: z.record(z.any()).nullable().optional(),
  error_message: z.string().nullable().optional(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  stage_runs: z.array(stageRunSchema).optional(),
});

export const flashcardSchema = z.object({
  front: z.string(),
  back: z.string(),
});

export const sourceSchema = z.object({
  document_type: z.string().nullable().optional(),
  page: z.number().nullable().optional(),
  chapter_name: z.string().nullable().optional(),
  preview: z.string().nullable().optional(),
});

export const retrievalDiagnosticsSchema = z.object({
  scope: scopeLiteralSchema,
  scope_id: z.string(),
  query: z.string(),
  total_candidates: z.number(),
  accepted_candidates: z.number(),
  best_score: z.number(),
  debug_trace_id: z.string().nullable().optional(),
  debug_artifact_path: z.string().nullable().optional(),
});

export const generateFlashcardsResponseSchema = z.object({
  flashcards: z.array(flashcardSchema),
  sources: z.array(sourceSchema).default([]),
  diagnostics: retrievalDiagnosticsSchema.nullable().optional(),
});

export const quizItemSchema = z.object({
  question: z.string(),
  options: z.array(z.string()),
  correct_answer: z.number(),
  explanation: z.string(),
  source: sourceSchema.nullable().optional(),
});

export const generateQuizResponseSchema = z.object({
  questions: z.array(quizItemSchema),
  diagnostics: retrievalDiagnosticsSchema.nullable().optional(),
});

export const chatAskResponseSchema = z.object({
  answer: z.string(),
  confidence: z.number(),
  citations: z.array(z.record(z.any())),
});

export const generatedHistoryItemSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  scope: scopeLiteralSchema,
  type: z.string(),
  created_at: z.string().nullable().optional(),
  subject_id: z.string().nullable().optional(),
  document_id: z.string().nullable().optional(),
  chapter_id: z.string().nullable().optional(),
  content_json: z.record(z.any()),
});

export const generatedHistoryResponseSchema = z.object({
  items: z.array(generatedHistoryItemSchema),
});

export type ScopeLiteral = z.infer<typeof scopeLiteralSchema>;
export type DocumentUploadResponse = z.infer<typeof documentUploadResponseSchema>;
export type JobResponse = z.infer<typeof jobSchema>;
export type GenerateFlashcardsResponse = z.infer<typeof generateFlashcardsResponseSchema>;
export type GenerateQuizResponse = z.infer<typeof generateQuizResponseSchema>;
export type ChatAskResponse = z.infer<typeof chatAskResponseSchema>;
export type GeneratedHistoryResponse = z.infer<typeof generatedHistoryResponseSchema>;
