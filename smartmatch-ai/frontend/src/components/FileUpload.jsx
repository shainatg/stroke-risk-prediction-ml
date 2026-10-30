import React, { useRef, useState } from 'react';
import {
  UploadCloud,
  FileText,
  FileCode,
  CheckCircle2,
  XCircle,
  RefreshCw,
  FolderOpen,
  AlertCircle
} from 'lucide-react';

export default function FileUpload({
  file,
  sampleFilename,
  onFileSelect,
  onSampleSelect,
  onRemoveFile,
  error,
  disabled,
  samples = []
}) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Drag and drop event handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      validateAndSelectFile(droppedFile);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  const validateAndSelectFile = (selectedFile) => {
    const allowed = ['pdf', 'docx', 'txt'];
    const ext = selectedFile.name.split('.').pop().toLowerCase();
    if (!allowed.includes(ext)) {
      alert(`Unsupported file type: .${ext}. Please upload a .pdf, .docx, or .txt file.`);
      return;
    }
    onFileSelect(selectedFile);
  };

  // Format file size nicely
  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Get color and icon based on file extension
  const getFileBadge = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    if (ext === 'pdf') {
      return { label: 'PDF', bg: 'bg-rose-100 text-rose-700 border-rose-200' };
    } else if (ext === 'docx') {
      return { label: 'DOCX', bg: 'bg-blue-100 text-blue-700 border-blue-200' };
    } else {
      return { label: 'TXT', bg: 'bg-emerald-100 text-emerald-700 border-emerald-200' };
    }
  };

  const activeFilename = file ? file.name : sampleFilename;
  const activeSize = file ? formatBytes(file.size) : 'Preloaded Sample';
  const badge = activeFilename ? getFileBadge(activeFilename) : null;

  return (
    <div className="card-soft rounded-2xl p-6 transition-all duration-200">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-sky-100 flex items-center justify-center text-sky-700">
            <UploadCloud className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              Upload Your Document
            </h2>
            <p className="text-xs text-slate-500">
              Supports PDF (.pdf), Word (.docx), and Plain Text (.txt) up to 16 MB
            </p>
          </div>
        </div>

        {/* Formats Supported Pill */}
        <span className="hidden sm:inline-block text-[11px] font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200">
          PDF • DOCX • TXT
        </span>
      </div>

      {/* Hidden native input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        disabled={disabled}
        onChange={handleFileInputChange}
        className="hidden"
      />

      {/* Case 1: A file is currently active (either uploaded or sample selected) */}
      {activeFilename ? (
        <div className="p-4 rounded-xl bg-sky-50/70 border border-sky-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-white border border-sky-200 flex items-center justify-center shadow-xs text-sky-600 shrink-0">
              <FileText className="w-6 h-6" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-slate-900 truncate">
                  {activeFilename}
                </span>
                {badge && (
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase ${badge.bg}`}>
                    {badge.label}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Ready for semantic analysis</span>
                <span>•</span>
                <span>{activeSize}</span>
              </p>
            </div>
          </div>

          {/* Action buttons: Replace or Remove */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              disabled={disabled}
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-sky-700 bg-white hover:bg-sky-100 border border-sky-300 rounded-lg transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Replace File</span>
            </button>
            <button
              type="button"
              disabled={disabled}
              onClick={onRemoveFile}
              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-red-700 bg-white hover:bg-red-50 border border-red-200 rounded-lg transition-colors cursor-pointer"
              title="Remove document"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Remove</span>
            </button>
          </div>
        </div>
      ) : (
        /* Case 2: Dropzone area when no file is selected */
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !disabled && fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-6 sm:p-8 text-center cursor-pointer transition-all duration-200 ${
            isDragging
              ? 'border-sky-500 bg-sky-50 scale-[1.01]'
              : error
              ? 'border-red-300 bg-red-50/20 hover:border-red-400'
              : 'border-sky-200 bg-sky-50/30 hover:border-sky-400 hover:bg-sky-50/60'
          }`}
        >
          <div className="w-14 h-14 rounded-2xl bg-white border border-sky-100 shadow-xs mx-auto flex items-center justify-center text-sky-600 mb-3">
            <UploadCloud className="w-7 h-7" />
          </div>

          <p className="text-sm font-semibold text-slate-800">
            <span className="text-sky-600 font-bold hover:underline">Click to browse</span> or drag & drop your file here
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Accepts PDF (.pdf), Microsoft Word (.docx), or Text (.txt)
          </p>

          <button
            type="button"
            disabled={disabled}
            className="mt-4 inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold text-sky-700 bg-white hover:bg-sky-50 border border-sky-200 rounded-xl shadow-xs transition-colors"
          >
            <FolderOpen className="w-3.5 h-3.5 text-sky-600" />
            <span>Browse Files</span>
          </button>
        </div>
      )}

      {/* Validation Error Banner */}
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 1-Click Educational Sample Documents Selector */}
      {samples.length > 0 && (
        <div className="mt-4 pt-4 border-t border-slate-100">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span className="font-medium text-slate-600">Don't have a document handy? Pick a sample:</span>
            <span className="text-[11px] text-slate-400">1-click test</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {samples.map((sample, idx) => {
              const isSelected = sampleFilename === sample.filename && !file;
              return (
                <button
                  key={idx}
                  type="button"
                  disabled={disabled}
                  onClick={() => onSampleSelect(sample)}
                  className={`text-left p-2.5 rounded-xl border text-xs transition-all flex items-center justify-between cursor-pointer ${
                    isSelected
                      ? 'bg-sky-100/80 border-sky-400 font-semibold text-sky-900 shadow-xs'
                      : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <FileCode className="w-3.5 h-3.5 text-sky-600 shrink-0" />
                    <span className="truncate">{sample.filename}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 uppercase font-mono ml-2 shrink-0">
                    {sample.extension}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
