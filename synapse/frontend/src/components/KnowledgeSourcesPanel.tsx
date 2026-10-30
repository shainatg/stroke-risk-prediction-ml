import React, { useState, useRef } from 'react';
import { 
  Upload, 
  FileText, 
  Table, 
  FileCode, 
  Trash2, 
  Check, 
  Search, 
  Sparkles, 
  Layers, 
  AlertCircle
} from 'lucide-react';
import { DocumentMeta, DocumentFormat, SampleCorpus } from '../types';

interface KnowledgeSourcesPanelProps {
  documents: DocumentMeta[];
  sampleCorpora: SampleCorpus[];
  activeDocumentId: string | null;
  onSelectDocument: (docId: string) => void;
  onUploadFile: (file: File) => Promise<void>;
  onLoadSample: (sampleName: string) => Promise<void>;
  onDeleteDocument: (docId: string) => Promise<void>;
  isUploading: boolean;
}

export const KnowledgeSourcesPanel: React.FC<KnowledgeSourcesPanelProps> = ({
  documents,
  sampleCorpora,
  activeDocumentId,
  onSelectDocument,
  onUploadFile,
  onLoadSample,
  onDeleteDocument,
  isUploading,
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    setErrorMessage(null);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      try {
        await onUploadFile(file);
      } catch (err: any) {
        setErrorMessage(err.message || 'Upload failed');
      }
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMessage(null);
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      try {
        await onUploadFile(file);
      } catch (err: any) {
        setErrorMessage(err.message || 'Upload failed');
      }
      e.target.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFormatIcon = (format: DocumentFormat) => {
    switch (format) {
      case 'pdf':
        return <FileText className="w-4 h-4 text-rose-400" />;
      case 'docx':
      case 'doc':
        return <FileText className="w-4 h-4 text-indigo" />;
      case 'csv':
        return <Table className="w-4 h-4 text-emerald-400" />;
      case 'txt':
      case 'md':
      default:
        return <FileCode className="w-4 h-4 text-cyan" />;
    }
  };

  const filteredDocs = documents.filter(d => 
    d.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full bg-background-secondary border-r border-surface-border">
      
      {/* Header */}
      <div className="p-4 border-b border-surface-border">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-sm font-semibold tracking-tight text-slate-100 flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan" />
            Knowledge Sources
          </h2>
          <span className="text-[11px] font-mono text-slate-400">
            {documents.length} loaded
          </span>
        </div>
        <p className="text-xs text-slate-400">
          Upload PDF, DOCX, TXT, or CSV to analyze.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">

        {/* Drag and Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-all duration-200 ${
            dragOver
              ? 'border-cyan bg-cyan/5 scale-[0.99]'
              : 'border-surface-border hover:border-slate-500 bg-surface-50/50 hover:bg-surface-50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc,.txt,.csv,.md"
            onChange={handleFileChange}
            className="hidden"
          />
          <div className="flex flex-col items-center gap-1.5">
            <div className="p-2 rounded-full bg-surface-100 border border-surface-border">
              <Upload className={`w-4 h-4 ${isUploading ? 'text-cyan animate-bounce' : 'text-slate-400'}`} />
            </div>
            <div className="text-xs font-medium text-slate-200">
              {isUploading ? 'Parsing Document...' : 'Drop document or click to browse'}
            </div>
            <p className="text-[11px] text-slate-500 font-mono">
              PDF, DOCX, TXT, CSV (Up to 25MB)
            </p>
          </div>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="p-2.5 rounded-md bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
            <div className="flex-1">{errorMessage}</div>
          </div>
        )}

        {/* Document Search */}
        {documents.length > 3 && (
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search uploaded files..."
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-surface-50 border border-surface-border rounded-md text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan"
            />
          </div>
        )}

        {/* Document Cards List */}
        <div className="space-y-2">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-500 px-1">
            Active Workspace Corpora
          </div>

          {filteredDocs.length === 0 && !isUploading && (
            <div className="text-center py-6 px-3 border border-surface-border rounded-lg bg-surface-50/30">
              <FileText className="w-6 h-6 mx-auto text-slate-600 mb-1.5" />
              <p className="text-xs text-slate-400">No documents in workspace</p>
              <p className="text-[11px] text-slate-500 mt-0.5">Upload a file or pick a sample corpus below.</p>
            </div>
          )}

          {filteredDocs.map((doc) => {
            const isSelected = doc.id === activeDocumentId;
            return (
              <div
                key={doc.id}
                onClick={() => onSelectDocument(doc.id)}
                className={`group relative p-3 rounded-lg border text-left cursor-pointer transition-all duration-200 ${
                  isSelected
                    ? 'bg-surface-100 border-cyan/40 shadow-subtle'
                    : 'bg-surface-50/70 hover:bg-surface-100 border-surface-border hover:border-surface-hover'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="p-1.5 rounded bg-surface-200/50 border border-surface-border shrink-0">
                      {getFormatIcon(doc.file_type)}
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-xs font-semibold text-slate-200 truncate group-hover:text-cyan transition-colors">
                        {doc.filename}
                      </h4>
                      <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono mt-0.5">
                        <span className="uppercase text-slate-500">{doc.file_type}</span>
                        <span>•</span>
                        <span>{formatFileSize(doc.file_size)}</span>
                        <span>•</span>
                        <span>{doc.total_pages} {doc.total_pages === 1 ? 'page' : 'pages'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 shrink-0">
                    {isSelected && (
                      <span className="p-1 rounded-full bg-cyan/10 border border-cyan/30 text-cyan">
                        <Check className="w-3 h-3" />
                      </span>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteDocument(doc.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-rose-400 rounded transition-all hover:bg-surface-200"
                      title="Remove from workspace"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div className="mt-2 pt-2 border-t border-surface-border/60 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span>{doc.word_count.toLocaleString()} words</span>
                  <span>{doc.chunk_count} passages</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Sample Corpora Section */}
        {sampleCorpora.length > 0 && (
          <div className="pt-2 border-t border-surface-border space-y-2">
            <div className="flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-wider text-slate-500 px-1">
              <Sparkles className="w-3 h-3 text-lavender" />
              Pre-loaded Research Corpora
            </div>
            
            <div className="space-y-1.5">
              {sampleCorpora.map((sample) => (
                <button
                  key={sample.id}
                  onClick={() => onLoadSample(sample.filename)}
                  className="w-full text-left p-2 rounded-md bg-surface-50 hover:bg-surface-100 border border-surface-border hover:border-lavender/40 text-xs transition-all flex items-center justify-between group"
                >
                  <div className="flex items-center gap-2 truncate">
                    {getFormatIcon(sample.file_type)}
                    <span className="text-slate-300 group-hover:text-slate-100 truncate text-[11px]">
                      {sample.filename}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase">
                    Load
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

      </div>

    </div>
  );
};
