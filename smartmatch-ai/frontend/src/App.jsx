import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import TextInput from './components/TextInput';
import FileUpload from './components/FileUpload';
import ActionButton from './components/ActionButton';
import ResultsCard from './components/ResultsCard';
import WorkflowSection from './components/WorkflowSection';
import HowItWorksModal from './components/HowItWorksModal';
import { AlertCircle } from 'lucide-react';

export default function App() {
  const [questionText, setQuestionText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [sampleFilename, setSampleFilename] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorText, setErrorText] = useState('');
  const [errorFile, setErrorFile] = useState('');
  const [apiError, setApiError] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [samplesList, setSamplesList] = useState([]);
  const [isExplainerOpen, setIsExplainerOpen] = useState(false);

  // Fetch preloaded educational sample files from backend
  useEffect(() => {
    fetch('/api/samples')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.samples) {
          setSamplesList(data.samples);
        }
      })
      .catch((err) => {
        console.warn('Could not load samples list:', err);
      });
  }, []);

  // Handlers for file selection
  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setSampleFilename('');
    setErrorFile('');
    setApiError('');
  };

  const handleSampleSelect = (sample) => {
    setSampleFilename(sample.filename);
    setSelectedFile(null);
    setErrorFile('');
    setApiError('');
    // Optionally autofill suggested query if input is currently empty
    if (!questionText.trim() && sample.suggested_query) {
      setQuestionText(sample.suggested_query);
      setErrorText('');
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setSampleFilename('');
  };

  const handleClearText = () => {
    setQuestionText('');
    setErrorText('');
  };

  const handleSelectSampleQuery = (q) => {
    setQuestionText(q);
    setErrorText('');
  };

  // Core Analyze Handler
  const handleAnalyze = async () => {
    // 1. Reset Errors
    setErrorText('');
    setErrorFile('');
    setApiError('');

    let hasError = false;

    // 2. Validate Question
    if (!questionText.trim()) {
      setErrorText('Please enter your question or text in the text box.');
      hasError = true;
    }

    // 3. Validate File
    if (!selectedFile && !sampleFilename) {
      setErrorFile('Please upload a document (.pdf, .docx, or .txt) before analyzing.');
      hasError = true;
    }

    if (hasError) return;

    // 4. Send request to Flask backend
    setIsLoading(true);
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append('text', questionText.trim());

    if (selectedFile) {
      formData.append('file', selectedFile);
    } else if (sampleFilename) {
      formData.append('sample_filename', sampleFilename);
    }

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || data.status === 'error') {
        throw new Error(data.message || 'An error occurred during analysis.');
      }

      setAnalysisResult(data);

      // Scroll smoothly to results card
      setTimeout(() => {
        const resultsEl = document.getElementById('results-section');
        if (resultsEl) {
          resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);

    } catch (err) {
      console.error('Analysis error:', err);
      setApiError(err.message || 'Failed to connect to the backend server. Please verify it is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeAgain = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col justify-between">
      {/* Background decoration */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-sky-200/40 rounded-full blur-3xl"></div>
        <div className="absolute top-1/3 -right-40 w-96 h-96 bg-blue-100/50 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 flex-1">
        {/* Header */}
        <Header onOpenExplainer={() => setIsExplainerOpen(true)} />

        {/* Main Interactive Workspace */}
        <main className="max-w-5xl mx-auto px-4 pb-12">
          
          {/* General API error banner if something goes wrong */}
          {apiError && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl text-sm text-red-700 flex items-center gap-3 shadow-xs">
              <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
              <div>
                <span className="font-bold">Analysis Failed: </span>
                {apiError}
              </div>
            </div>
          )}

          {/* Top Grid: Left = Text Input, Right = File Upload */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
            {/* Section 1: Text Input */}
            <TextInput
              value={questionText}
              onChange={(val) => {
                setQuestionText(val);
                if (errorText) setErrorText('');
              }}
              onClear={handleClearText}
              error={errorText}
              disabled={isLoading}
              onSelectSampleQuery={handleSelectSampleQuery}
            />

            {/* Section 2: File Upload */}
            <FileUpload
              file={selectedFile}
              sampleFilename={sampleFilename}
              onFileSelect={handleFileSelect}
              onSampleSelect={handleSampleSelect}
              onRemoveFile={handleRemoveFile}
              error={errorFile}
              disabled={isLoading}
              samples={samplesList}
            />
          </div>

          {/* Section 3: Analyze Button */}
          <div className="mt-8">
            <ActionButton
              onClick={handleAnalyze}
              isLoading={isLoading}
              disabled={isLoading}
            />
          </div>

          {/* Section 4: Results Card (Shown after analysis) */}
          {analysisResult && (
            <ResultsCard
              result={analysisResult}
              onAnalyzeAgain={handleAnalyzeAgain}
            />
          )}

          {/* Section 5: Simple 4-Step Workflow at Bottom */}
          <WorkflowSection />
        </main>
      </div>

      {/* Educational Explainer Modal */}
      <HowItWorksModal
        isOpen={isExplainerOpen}
        onClose={() => setIsExplainerOpen(false)}
      />

      {/* Footer */}
      <footer className="w-full py-6 text-center text-xs text-slate-500 border-t border-sky-100/80 bg-white/50 backdrop-blur-xs relative z-10">
        <p>
          <strong>SmartMatch AI</strong> • Built with React, Vite, Tailwind CSS, Flask & Scikit-learn
        </p>
        <p className="text-[11px] text-slate-400 mt-1">
          Demonstrates TF-IDF Vectorization, PyMuPDF Document Extraction, and Cosine Similarity Matching
        </p>
      </footer>
    </div>
  );
}
