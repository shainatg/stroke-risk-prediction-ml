import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { ThreePanelLayout } from './components/ThreePanelLayout';
import { KnowledgeSourcesPanel } from './components/KnowledgeSourcesPanel';
import { QueryStudioPanel } from './components/QueryStudioPanel';
import { ResultsPanel } from './components/ResultsPanel';
import { SimilarityLabModal } from './components/SimilarityLabModal';
import { DocumentViewerModal } from './components/DocumentViewerModal';
import { PipelineExplorerModal } from './components/PipelineExplorerModal';
import { HistoryDrawer } from './components/HistoryDrawer';
import { ShortcutsModal } from './components/ShortcutsModal';

import { api } from './services/api';
import { 
  DocumentMeta, 
  DocumentDetail, 
  AnalysisResult, 
  AnalysisHistoryItem, 
  PipelineStage,
  SampleCorpus,
  Chunk,
  TimelineStep
} from './types';

export function App() {
  // Connection and metadata
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [sampleCorpora, setSampleCorpora] = useState<SampleCorpus[]>([]);
  const [activeDocId, setActiveDocId] = useState<string | null>(null);
  const [activeDocDetail, setActiveDocDetail] = useState<DocumentDetail | null>(null);

  // Studio and Analysis
  const [query, setQuery] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [timeline, setTimeline] = useState<TimelineStep[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [recentQueries, setRecentQueries] = useState<string[]>([]);

  // Hyperparameters
  const [chunkSize, setChunkSize] = useState<number>(25);
  const [chunkOverlap, setChunkOverlap] = useState<number>(6);
  const [topK, setTopK] = useState<number>(5);

  // Modals & Drawers
  const [isSimilarityLabOpen, setIsSimilarityLabOpen] = useState<boolean>(false);
  const [isDocViewerOpen, setIsDocViewerOpen] = useState<boolean>(false);
  const [isPipelineOpen, setIsPipelineOpen] = useState<boolean>(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState<boolean>(false);
  const [highlightChunk, setHighlightChunk] = useState<Chunk | null>(null);

  // History & Pipeline
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [stages, setStages] = useState<PipelineStage[]>([]);

  // 1. Initial Load
  const initApp = useCallback(async () => {
    try {
      const health = await api.getHealth();
      setBackendOnline(health.status === 'online');

      const docsData = await api.listDocuments();
      setDocuments(docsData.documents);
      setSampleCorpora(docsData.sample_corpora);

      const hist = await api.getHistory();
      setHistory(hist);

      const pipe = await api.getPipelineInfo();
      setStages(pipe.stages);

      // If no document exists in database, auto-load first sample document
      if (docsData.documents.length === 0 && docsData.sample_corpora.length > 0) {
        const firstSample = docsData.sample_corpora[0];
        const loaded = await api.loadSampleDocument(firstSample.filename);
        setDocuments([loaded]);
        setActiveDocId(loaded.id);
        const detail = await api.getDocument(loaded.id);
        setActiveDocDetail(detail);
      } else if (docsData.documents.length > 0) {
        setActiveDocId(docsData.documents[0].id);
        const detail = await api.getDocument(docsData.documents[0].id);
        setActiveDocDetail(detail);
      }
    } catch (err) {
      console.error('Initialization error:', err);
      setBackendOnline(false);
    }
  }, []);

  useEffect(() => {
    initApp();
  }, [initApp]);

  // Global Keyboard shortcuts
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsSimilarityLabOpen(false);
        setIsDocViewerOpen(false);
        setIsPipelineOpen(false);
        setIsHistoryOpen(false);
        setIsShortcutsOpen(false);
      }
      if (e.key === '?' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        setIsShortcutsOpen(true);
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  // 2. Select Active Document
  const handleSelectDocument = async (docId: string) => {
    setActiveDocId(docId);
    try {
      const detail = await api.getDocument(docId);
      setActiveDocDetail(detail);
    } catch (err) {
      console.error('Failed to load document detail:', err);
    }
  };

  // 3. Upload File
  const handleUploadFile = async (file: File) => {
    setIsUploading(true);
    try {
      const newDoc = await api.uploadDocument(file, chunkSize, chunkOverlap);
      setDocuments(prev => [newDoc, ...prev]);
      setActiveDocId(newDoc.id);
      const detail = await api.getDocument(newDoc.id);
      setActiveDocDetail(detail);
    } finally {
      setIsUploading(false);
    }
  };

  // 4. Load Sample Corpus
  const handleLoadSample = async (sampleName: string) => {
    setIsUploading(true);
    try {
      const newDoc = await api.loadSampleDocument(sampleName, chunkSize, chunkOverlap);
      setDocuments(prev => [newDoc, ...prev.filter(d => d.id !== newDoc.id)]);
      setActiveDocId(newDoc.id);
      const detail = await api.getDocument(newDoc.id);
      setActiveDocDetail(detail);
    } finally {
      setIsUploading(false);
    }
  };

  // 5. Delete Document
  const handleDeleteDocument = async (docId: string) => {
    try {
      await api.deleteDocument(docId);
      setDocuments(prev => prev.filter(d => d.id !== docId));
      if (activeDocId === docId) {
        const remaining = documents.filter(d => d.id !== docId);
        if (remaining.length > 0) {
          handleSelectDocument(remaining[0].id);
        } else {
          setActiveDocId(null);
          setActiveDocDetail(null);
        }
      }
    } catch (err) {
      console.error('Failed to delete document:', err);
    }
  };

  // 6. Execute Semantic Analysis
  const handleAnalyze = async () => {
    if (!activeDocId || !query.trim()) return;

    setIsAnalyzing(true);
    // Initialize timeline steps
    setTimeline([
      { step: 1, name: "Document received", status: "active", duration_ms: 0, detail: "Validating document stream..." }
    ]);

    try {
      const res = await api.analyze({
        document_id: activeDocId,
        query: query.trim(),
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap,
        top_k: topK
      });

      setAnalysis(res);
      setTimeline(res.timeline);
      
      // Update recent queries
      setRecentQueries(prev => [query.trim(), ...prev.filter(q => q !== query.trim())].slice(0, 10));

      // Refresh history list
      const hist = await api.getHistory();
      setHistory(hist);
    } catch (err: any) {
      console.error('Analysis error:', err);
      alert(`Analysis Failed: ${err.message || 'Server error'}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 7. Select History Item
  const handleSelectHistoryItem = async (id: string) => {
    try {
      const record = await api.getHistoryItem(id);
      if (record.full_result) {
        setAnalysis(record.full_result);
        setQuery(record.full_result.query);
        setTimeline(record.full_result.timeline || []);
        if (record.full_result.document_id) {
          handleSelectDocument(record.full_result.document_id);
        }
      }
    } catch (err) {
      console.error('Failed to reopen history item:', err);
    }
  };

  // 8. Delete History Item
  const handleDeleteHistoryItem = async (id: string) => {
    try {
      await api.deleteHistoryItem(id);
      setHistory(prev => prev.filter(h => h.id !== id));
    } catch (err) {
      console.error('Failed to delete history item:', err);
    }
  };

  // 9. Download PDF Report
  const handleDownloadPdf = (analysisId: string) => {
    const url = api.getPdfReportUrl(analysisId);
    window.open(url, '_blank');
  };

  const activeDoc = documents.find(d => d.id === activeDocId) || null;

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans select-none">
      
      {/* Top Navigation */}
      <Navbar
        backendOnline={backendOnline}
        onOpenSimilarityLab={() => setIsSimilarityLabOpen(true)}
        onOpenDocumentViewer={() => setIsDocViewerOpen(true)}
        onOpenPipelineExplorer={() => setIsPipelineOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onOpenShortcuts={() => setIsShortcutsOpen(true)}
        activeDocName={activeDoc?.filename}
        hasAnalysis={!!analysis}
      />

      {/* Three Panel Studio Workspace */}
      <ThreePanelLayout
        hasAnalysis={!!analysis}
        leftPanel={
          <KnowledgeSourcesPanel
            documents={documents}
            sampleCorpora={sampleCorpora}
            activeDocumentId={activeDocId}
            onSelectDocument={handleSelectDocument}
            onUploadFile={handleUploadFile}
            onLoadSample={handleLoadSample}
            onDeleteDocument={handleDeleteDocument}
            isUploading={isUploading}
          />
        }
        centerPanel={
          <QueryStudioPanel
            query={query}
            setQuery={setQuery}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
            activeDoc={activeDoc}
            timeline={timeline}
            totalDurationMs={analysis?.duration_ms}
            recentQueries={recentQueries}
            onSelectRecentQuery={(q) => setQuery(q)}
            chunkSize={chunkSize}
            setChunkSize={setChunkSize}
            chunkOverlap={chunkOverlap}
            setChunkOverlap={setChunkOverlap}
            topK={topK}
            setTopK={setTopK}
          />
        }
        rightPanel={
          <ResultsPanel
            analysis={analysis}
            onOpenSimilarityLab={() => setIsSimilarityLabOpen(true)}
            onOpenDocumentViewer={() => setIsDocViewerOpen(true)}
            onSelectPassageForViewer={(chunk) => setHighlightChunk(chunk)}
            onDownloadPdf={handleDownloadPdf}
          />
        }
      />

      {/* Modals & Drawers */}
      <SimilarityLabModal
        isOpen={isSimilarityLabOpen}
        onClose={() => setIsSimilarityLabOpen(false)}
        analysis={analysis}
        onLocateInViewer={(chunk) => {
          setHighlightChunk(chunk);
          setIsDocViewerOpen(true);
        }}
      />

      <DocumentViewerModal
        isOpen={isDocViewerOpen}
        onClose={() => setIsDocViewerOpen(false)}
        document={activeDocDetail}
        highlightChunk={highlightChunk}
      />

      <PipelineExplorerModal
        isOpen={isPipelineOpen}
        onClose={() => setIsPipelineOpen(false)}
        stages={stages}
      />

      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={history}
        onSelectHistoryItem={handleSelectHistoryItem}
        onDeleteHistoryItem={handleDeleteHistoryItem}
        onSearchHistory={(search) => {
          api.getHistory(search).then(setHistory).catch(console.error);
        }}
      />

      <ShortcutsModal
        isOpen={isShortcutsOpen}
        onClose={() => setIsShortcutsOpen(false)}
      />

    </div>
  );
}

export default App;
