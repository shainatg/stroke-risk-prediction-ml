import type { 
  DocumentMeta, 
  DocumentDetail, 
  AnalysisResult, 
  AnalysisHistoryItem, 
  PipelineStage,
  SampleCorpus
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '';

export const api = {
  async getHealth(): Promise<{ status: string; version: string; embedding_dimension: number }> {
    const res = await fetch(`${BASE_URL}/api/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  },

  async listDocuments(): Promise<{ documents: DocumentMeta[]; sample_corpora: SampleCorpus[] }> {
    const res = await fetch(`${BASE_URL}/api/documents`);
    if (!res.ok) throw new Error('Failed to fetch documents list');
    return res.json();
  },

  async uploadDocument(file: File, chunkSize = 25, chunkOverlap = 6): Promise<DocumentMeta> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('chunk_size', chunkSize.toString());
    formData.append('chunk_overlap', chunkOverlap.toString());

    const res = await fetch(`${BASE_URL}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to upload document');
    }
    const data = await res.json();
    return {
      id: data.document_id,
      filename: data.filename,
      file_type: data.file_type,
      file_size: data.file_size,
      word_count: data.word_count,
      char_count: data.char_count,
      chunk_count: data.chunk_count,
      total_pages: data.total_pages,
    };
  },

  async loadSampleDocument(sampleName: string, chunkSize = 25, chunkOverlap = 6): Promise<DocumentMeta> {
    const url = `${BASE_URL}/api/documents/load-sample?sample_name=${encodeURIComponent(sampleName)}&chunk_size=${chunkSize}&chunk_overlap=${chunkOverlap}`;
    const res = await fetch(url, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to load sample document');
    }
    const data = await res.json();
    return {
      id: data.document_id,
      filename: data.filename,
      file_type: data.file_type,
      file_size: data.file_size,
      word_count: data.word_count,
      char_count: data.char_count,
      chunk_count: data.chunk_count,
      total_pages: data.total_pages,
    };
  },

  async getDocument(docId: string): Promise<DocumentDetail> {
    const res = await fetch(`${BASE_URL}/api/documents/${docId}`);
    if (!res.ok) throw new Error('Failed to fetch document details');
    return res.json();
  },

  async deleteDocument(docId: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/api/documents/${docId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  async analyze(params: {
    document_id: string;
    query: string;
    chunk_size?: number;
    chunk_overlap?: number;
    top_k?: number;
  }): Promise<AnalysisResult> {
    const res = await fetch(`${BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_id: params.document_id,
        query: params.query,
        chunk_size: params.chunk_size ?? 25,
        chunk_overlap: params.chunk_overlap ?? 6,
        top_k: params.top_k ?? 5,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Semantic analysis failed');
    }
    return res.json();
  },

  async getHistory(search?: string): Promise<AnalysisHistoryItem[]> {
    const q = search ? `?search=${encodeURIComponent(search)}` : '';
    const res = await fetch(`${BASE_URL}/api/history${q}`);
    if (!res.ok) throw new Error('Failed to fetch history');
    const data = await res.json();
    return data.analyses;
  },

  async getHistoryItem(id: string): Promise<{ full_result: AnalysisResult }> {
    const res = await fetch(`${BASE_URL}/api/history/${id}`);
    if (!res.ok) throw new Error('Failed to fetch history record');
    return res.json();
  },

  async deleteHistoryItem(id: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/api/history/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete history item');
  },

  async getPipelineInfo(): Promise<{ stages: PipelineStage[] }> {
    const res = await fetch(`${BASE_URL}/api/pipeline/info`);
    if (!res.ok) throw new Error('Failed to fetch pipeline specifications');
    return res.json();
  },

  getPdfReportUrl(analysisId: string): string {
    return `${BASE_URL}/api/export/pdf/${analysisId}`;
  }
};
