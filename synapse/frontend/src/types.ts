export type DocumentFormat = 'pdf' | 'docx' | 'txt' | 'csv' | 'md' | 'doc';

export interface DocumentMeta {
  id: string;
  filename: string;
  file_type: DocumentFormat;
  file_size: number;
  char_count: number;
  word_count: number;
  chunk_count: number;
  total_pages: number;
  created_at?: number;
  is_sample?: boolean;
}

export interface DocumentPage {
  page: number;
  text: string;
  start_char: number;
  end_char: number;
  char_count: number;
  word_count: number;
}

export interface Chunk {
  index: number;
  text: string;
  wordCount: number;
  charCount: number;
  startWord?: number;
  endWord?: number;
  page: number;
  charStart?: number;
  charEnd?: number;
  score?: number;
  score_percentage?: number;
  vector_preview?: number[];
  overlapNext?: string;
}

export interface DocumentDetail extends DocumentMeta {
  full_text: string;
  pages: DocumentPage[];
  chunks: Chunk[];
}

export interface TimelineStep {
  step: number;
  name: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  duration_ms: number;
  detail: string;
}

export interface MatchCitation {
  passage_index: number;
  page: number;
  similarity_score: number;
  similarity_pct: string;
  quote: string;
}

export interface MatchExplanation {
  similarity_score: number;
  similarity_percentage: number;
  exact_term_matches: string[];
  stem_matches: string[];
  dot_product: number;
  top_contributing_dimensions: Array<{
    dimension: number;
    contribution: number;
  }>;
  explanation: string;
}

export interface ProjectionPoint {
  id: string;
  type: 'query' | 'chunk';
  label: string;
  x: number;
  y: number;
  score: number;
  page: number;
  preview: string;
}

export interface Projection2D {
  available: boolean;
  method?: string;
  variance_explained?: number[];
  points: ProjectionPoint[];
}

export interface AnalysisResult {
  analysis_id?: string;
  query: string;
  document_id: string;
  document_name: string;
  document_type: DocumentFormat;
  total_document_pages: number;
  total_document_words: number;
  total_chunks_analyzed: number;
  duration_ms: number;
  timeline: TimelineStep[];
  top_score: number;
  top_score_percentage: string;
  top_page: number;
  top_passage_index: number;
  top_passage_text: string;
  ranked_chunks: Chunk[];
  grounded_answer: string;
  key_insight: string;
  citations: MatchCitation[];
  normal_llm_answer: string;
  match_explanation: MatchExplanation;
  projection_2d: Projection2D;
  query_vector_slice?: number[];
  top_chunk_vector_slice?: number[];
}

export interface AnalysisHistoryItem {
  id: string;
  document_id: string;
  document_name: string;
  query: string;
  key_insight: string;
  top_score: number;
  top_chunk_index: number;
  top_page: number;
  top_passage_text: string;
  duration_ms: number;
  created_at: number;
}

export interface PipelineStage {
  id: string;
  name: string;
  phase: string;
  description: string;
  technical_details: string;
  formula: string;
}

export interface SampleCorpus {
  id: string;
  filename: string;
  file_type: DocumentFormat;
  file_size: number;
  is_sample: boolean;
}
